"""
Health Records Service

Offline-first health records management with versioning and conflict resolution.
Supports medical history, prescriptions, and lab reports.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from google.cloud.firestore import AsyncClient
import logging

from app.records.schemas import RecordType, ConflictResolutionRequest

logger = logging.getLogger(__name__)


class HealthRecordsService:
    """Service for health records management."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.records_collection = db.collection("health_records")
        self.audit_collection = db.collection("health_records_audit")
    
    async def create_record(
        self,
        user_id: str,
        record_type: RecordType,
        data: Dict[str, Any],
        client_version: int,
        created_by: Optional[str] = None
    ) -> dict:
        """
        Create a new health record with versioning.
        
        Args:
            user_id: Patient user ID
            record_type: Type of record
            data: Record data
            client_version: Client-side version number
            created_by: User ID who created the record
            
        Returns:
            Created record document
        """
        # Check for conflicts if client_version > 1
        if client_version > 1:
            # Get latest server version
            latest_query = (
                self.records_collection
                .where("user_id", "==", user_id)
                .where("record_type", "==", record_type.value)
                .where("is_deleted", "==", False)
                .order_by("version", direction="DESCENDING")
                .limit(1)
            )
            
            latest_docs = [doc async for doc in latest_query.stream()]
            if latest_docs:
                latest_version = latest_docs[0].to_dict().get("version", 0)
                if client_version <= latest_version:
                    # Conflict detected
                    return {
                        "id": None,
                        "conflict": True,
                        "server_version": latest_version,
                        "client_version": client_version
                    }
        
        # Create new record
        record_data = {
            "user_id": user_id,
            "record_type": record_type.value,
            "data": data,
            "version": client_version,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": created_by or user_id,
            "is_deleted": False,
            "sync_status": "synced"
        }
        
        doc_ref = self.records_collection.document()
        await doc_ref.set(record_data)
        
        # Create audit trail
        await self._create_audit_entry(
            record_id=doc_ref.id,
            action="create",
            user_id=user_id,
            data=record_data
        )
        
        record_data["id"] = doc_ref.id
        logger.info(f"Health record created: {doc_ref.id} for user {user_id}")
        
        return record_data
    
    async def get_record(self, record_id: str, user_id: str) -> Optional[dict]:
        """
        Get a specific health record.
        
        Args:
            record_id: Record document ID
            user_id: User ID (for authorization)
            
        Returns:
            Record document or None
        """
        doc_ref = self.records_collection.document(record_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            return None
        
        record_data = doc.to_dict()
        
        # Verify ownership
        if record_data.get("user_id") != user_id:
            return None
        
        record_data["id"] = doc.id
        return record_data
    
    async def list_records(
        self,
        user_id: str,
        record_type: Optional[RecordType] = None,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False
    ) -> dict:
        """
        List health records for a user with pagination.
        
        Args:
            user_id: Patient user ID
            record_type: Optional filter by record type
            page: Page number (1-indexed)
            page_size: Number of records per page
            include_deleted: Include deleted records
            
        Returns:
            Dictionary with records list and pagination info
        """
        query = self.records_collection.where("user_id", "==", user_id)
        
        if record_type:
            query = query.where("record_type", "==", record_type.value)
        
        if not include_deleted:
            query = query.where("is_deleted", "==", False)
        
        # Order by updated_at descending
        query = query.order_by("updated_at", direction="DESCENDING")
        
        # Pagination
        offset = (page - 1) * page_size
        query = query.limit(page_size).offset(offset)
        
        records = []
        async for doc in query.stream():
            record_data = doc.to_dict()
            record_data["id"] = doc.id
            records.append(record_data)
        
        # Get total count (simplified - in production, use a counter)
        count_query = self.records_collection.where("user_id", "==", user_id)
        if record_type:
            count_query = count_query.where("record_type", "==", record_type.value)
        if not include_deleted:
            count_query = count_query.where("is_deleted", "==", False)
        
        total = sum(1 async for _ in count_query.stream())
        
        return {
            "records": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total
        }
    
    async def update_record(
        self,
        record_id: str,
        user_id: str,
        update_data: Dict[str, Any],
        client_version: int
    ) -> Optional[dict]:
        """
        Update a health record with conflict detection.
        
        Args:
            record_id: Record document ID
            user_id: User ID (for authorization)
            update_data: Data to update
            client_version: Client-side version number
            
        Returns:
            Updated record or conflict info
        """
        # Get current record
        record = await self.get_record(record_id, user_id)
        if not record:
            return None
        
        server_version = record.get("version", 0)
        
        # Conflict detection
        if client_version <= server_version:
            return {
                "id": record_id,
                "conflict": True,
                "server_version": server_version,
                "client_version": client_version,
                "server_data": record
            }
        
        # Update record
        update_fields = {
            "data": {**record.get("data", {}), **update_data},
            "version": client_version,
            "updated_at": datetime.utcnow(),
            "sync_status": "synced"
        }
        
        await self.records_collection.document(record_id).update(update_fields)
        
        # Audit trail
        await self._create_audit_entry(
            record_id=record_id,
            action="update",
            user_id=user_id,
            data=update_fields
        )
        
        # Return updated record
        updated_record = await self.get_record(record_id, user_id)
        logger.info(f"Health record updated: {record_id}")
        
        return updated_record
    
    async def delete_record(
        self,
        record_id: str,
        user_id: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a health record (soft delete by default).
        
        Args:
            record_id: Record document ID
            user_id: User ID (for authorization)
            soft_delete: If True, mark as deleted; if False, permanently delete
            
        Returns:
            True if successful
        """
        record = await self.get_record(record_id, user_id)
        if not record:
            return False
        
        if soft_delete:
            # Soft delete
            await self.records_collection.document(record_id).update({
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            await self._create_audit_entry(
                record_id=record_id,
                action="delete",
                user_id=user_id,
                data={"soft_delete": True}
            )
        else:
            # Hard delete
            await self.records_collection.document(record_id).delete()
            
            await self._create_audit_entry(
                record_id=record_id,
                action="hard_delete",
                user_id=user_id,
                data={}
            )
        
        logger.info(f"Health record deleted: {record_id}")
        return True
    
    async def resolve_conflict(
        self,
        conflict_request: ConflictResolutionRequest,
        user_id: str
    ) -> Optional[dict]:
        """
        Resolve a sync conflict by choosing a version.
        
        Args:
            conflict_request: Conflict resolution request
            user_id: User ID (for authorization)
            
        Returns:
            Resolved record
        """
        record = await self.get_record(conflict_request.record_id, user_id)
        if not record:
            return None
        
        # Update with resolved data
        resolved_data = {
            "data": conflict_request.resolved_data,
            "version": record.get("version", 0) + 1,
            "updated_at": datetime.utcnow(),
            "sync_status": "synced",
            "conflict_resolved_at": datetime.utcnow()
        }
        
        await self.records_collection.document(conflict_request.record_id).update(resolved_data)
        
        await self._create_audit_entry(
            record_id=conflict_request.record_id,
            action="resolve_conflict",
            user_id=user_id,
            data={
                "chosen_version": conflict_request.chosen_version,
                "resolved_data": conflict_request.resolved_data
            }
        )
        
        logger.info(f"Conflict resolved for record: {conflict_request.record_id}")
        
        return await self.get_record(conflict_request.record_id, user_id)
    
    async def get_pending_sync_records(self, user_id: str) -> List[dict]:
        """
        Get records that need to be synced (for offline-first support).
        
        Args:
            user_id: User ID
            
        Returns:
            List of records with pending sync status
        """
        query = (
            self.records_collection
            .where("user_id", "==", user_id)
            .where("sync_status", "==", "pending")
        )
        
        records = []
        async for doc in query.stream():
            record_data = doc.to_dict()
            record_data["id"] = doc.id
            records.append(record_data)
        
        return records
    
    async def _create_audit_entry(
        self,
        record_id: str,
        action: str,
        user_id: str,
        data: Dict[str, Any]
    ):
        """Create an immutable audit trail entry."""
        audit_data = {
            "record_id": record_id,
            "action": action,
            "user_id": user_id,
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
        await self.audit_collection.add(audit_data)

