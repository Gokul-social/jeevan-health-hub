# Firestore Database Schemas

This document describes the Firestore collection structures for the Jeevan+ backend.

## Collections

### `users`
User accounts (patients, doctors, admins).

```javascript
{
  id: "user_doc_id",
  phone: "encrypted_phone",           // AES-256 encrypted
  email: "encrypted_email",            // AES-256 encrypted
  password_hash: "bcrypt_hash",
  full_name: "John Doe",
  role: "patient" | "doctor" | "admin",
  is_verified: boolean,
  is_active: boolean,
  date_of_birth: "YYYY-MM-DD",
  gender: "male" | "female" | "other",
  address: "string",
  emergency_contact_name: "string",
  emergency_contact_phone: "encrypted_phone",
  // Doctor-specific fields
  specialization: "string",
  license_number: "encrypted",         // AES-256 encrypted
  years_of_experience: number,
  bio: "string",
  consultation_fee: number,
  created_at: Timestamp,
  updated_at: Timestamp,
  version: number                      // For offline sync
}
```

**Indexes Required:**
- `is_active` (ascending)
- `role` (ascending)

### `family_links`
Links between patients and family members.

```javascript
{
  id: "link_doc_id",
  patient_id: "user_id",
  family_member_id: "user_id",
  relationship: "spouse" | "child" | "parent" | "sibling" | "other",
  created_at: Timestamp
}
```

**Indexes Required:**
- `patient_id` (ascending)
- `family_member_id` (ascending)

### `health_records`
Medical records (history, prescriptions, lab reports).

```javascript
{
  id: "record_doc_id",
  user_id: "user_id",
  record_type: "medical_history" | "prescription" | "lab_report" | "vital_sign" | "diagnosis" | "treatment",
  data: {
    // Record-type specific data
    title: "string",
    description: "string",
    condition: "string",
    // ... other fields
  },
  version: number,                     // For conflict resolution
  created_at: Timestamp,
  updated_at: Timestamp,
  created_by: "user_id",
  is_deleted: boolean,
  deleted_at: Timestamp | null,
  sync_status: "synced" | "pending" | "conflict",
  conflict_resolved_at: Timestamp | null
}
```

**Indexes Required:**
- `user_id` + `record_type` + `is_deleted` (composite)
- `user_id` + `updated_at` (descending)
- `user_id` + `sync_status`

### `health_records_audit`
Immutable audit trail for health records.

```javascript
{
  id: "audit_doc_id",
  record_id: "record_doc_id",
  action: "create" | "update" | "delete" | "resolve_conflict",
  user_id: "user_id",
  data: {},                            // Action-specific data
  timestamp: Timestamp
}
```

**Indexes Required:**
- `record_id` + `timestamp` (descending)

### `consultations`
Telemedicine consultation sessions.

```javascript
{
  id: "consultation_doc_id",
  doctor_id: "user_id",
  patient_id: "user_id",
  status: "scheduled" | "active" | "completed" | "cancelled" | "missed",
  consultation_type: "video" | "audio" | "text",
  scheduled_time: Timestamp | null,
  started_at: Timestamp | null,
  ended_at: Timestamp | null,
  reason: "string",
  notes: "string",
  session_token: "encrypted_token",    // Encrypted session token
  webrtc_config: {
    stun_servers: [],
    turn_servers: [],
    // ... WebRTC config
  },
  created_at: Timestamp,
  updated_at: Timestamp
}
```

**Indexes Required:**
- `doctor_id` + `status`
- `patient_id` + `status`
- `status` + `scheduled_time`

### `webrtc_signaling`
WebRTC signaling messages (offer, answer, ICE candidates).

```javascript
{
  id: "signal_doc_id",
  consultation_id: "consultation_id",
  from_user_id: "user_id",
  to_user_id: "user_id",
  signal_type: "offer" | "answer" | "ice-candidate",
  signal_data: {},                    // WebRTC signal payload
  timestamp: Timestamp,
  delivered: boolean
}
```

**Indexes Required:**
- `consultation_id` + `to_user_id` + `delivered`
- `consultation_id` + `timestamp`

### `pharmacies`
Pharmacy information.

```javascript
{
  id: "pharmacy_doc_id",
  name: "string",
  address: "string",
  city: "string",
  state: "string",
  pincode: "string",
  phone: "string",
  email: "string",
  latitude: number,
  longitude: number,
  operating_hours: {},                // Day-wise hours
  is_24x7: boolean,
  created_at: Timestamp,
  updated_at: Timestamp
}
```

**Indexes Required:**
- `city` + `state`
- `pincode`

### `medicine_stock`
Medicine stock information per pharmacy.

```javascript
{
  id: "stock_doc_id",
  pharmacy_id: "pharmacy_id",
  medicine_name: "string",             // Lowercase for search
  quantity: number,
  unit: "units" | "strips" | "bottles",
  expiry_date: "YYYY-MM-DD",
  price: number,
  manufacturer: "string",
  created_at: Timestamp,
  updated_at: Timestamp,
  last_restocked: Timestamp
}
```

**Indexes Required:**
- `pharmacy_id` + `medicine_name`
- `medicine_name` + `quantity`

### `low_stock_alerts`
Low stock alerts for pharmacies.

```javascript
{
  id: "alert_doc_id",
  pharmacy_id: "pharmacy_id",
  medicine_name: "string",
  current_quantity: number,
  threshold: number,
  alert_level: "warning" | "critical",
  created_at: Timestamp,
  resolved: boolean
}
```

**Indexes Required:**
- `pharmacy_id` + `resolved`
- `resolved` + `created_at`

### `iot_devices`
IoT device registration and authentication.

```javascript
{
  id: "device_id",
  user_id: "user_id",
  token: "device_auth_token",         // Hashed in production
  device_type: "string",
  is_active: boolean,
  registered_at: Timestamp,
  last_seen: Timestamp
}
```

**Indexes Required:**
- `user_id` + `is_active`

### `vital_data`
IoT vital sign measurements.

```javascript
{
  id: "vital_doc_id",
  user_id: "user_id",
  device_id: "device_id",
  timestamp: Timestamp,
  heart_rate: number,                  // BPM
  systolic_bp: number,                // mmHg
  diastolic_bp: number,               // mmHg
  spo2: number,                       // Percentage
  temperature: number,                // Celsius
  glucose: number,                    // mg/dL
  weight: number,                     // kg
  alerts: ["string"],                 // Generated alerts
  metadata: {},
  created_at: Timestamp
}
```

**Indexes Required:**
- `user_id` + `timestamp` (descending)
- `device_id` + `timestamp` (descending)
- `user_id` + `created_at` (descending)

### `vital_alerts`
Vital sign threshold alerts.

```javascript
{
  id: "alert_doc_id",
  user_id: "user_id",
  device_id: "device_id",
  vital_data_id: "vital_doc_id",
  alert_message: "string",
  alert_level: "warning" | "critical",
  timestamp: Timestamp,
  created_at: Timestamp,
  resolved: boolean,
  resolved_at: Timestamp | null
}
```

**Indexes Required:**
- `user_id` + `resolved` + `created_at` (descending)

## Security Rules (Firestore)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Health records - users can only access their own
    match /health_records/{recordId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Consultations - only participants can access
    match /consultations/{consultationId} {
      allow read, write: if request.auth != null && 
        (resource.data.doctor_id == request.auth.uid || 
         resource.data.patient_id == request.auth.uid);
    }
    
    // Public read for pharmacies, authenticated write
    match /pharmacies/{pharmacyId} {
      allow read: if true;
      allow write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Public read for medicine stock
    match /medicine_stock/{stockId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## Notes

1. **Encryption**: Sensitive fields (phone, email, license numbers) are encrypted at the application level using AES-256-GCM before storage.

2. **Versioning**: Health records use version numbers for offline-first conflict resolution.

3. **Soft Deletes**: Records are soft-deleted (is_deleted flag) to maintain audit trail.

4. **Indexes**: All composite queries require corresponding Firestore indexes. Create them via Firebase Console or `firebase.json`.

5. **Timestamps**: All timestamps use Firestore Timestamp type for proper querying and sorting.

6. **Case Sensitivity**: Medicine names are stored in lowercase for case-insensitive search.

