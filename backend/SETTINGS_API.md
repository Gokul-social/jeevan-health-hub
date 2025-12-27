# Settings API Reference

Complete API endpoints for user settings management in Jeevan+ backend.

## Base URL
```
/api/settings
```

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

## Get All Settings

Get complete user settings including preferences, storage, and security info.

**Endpoint:** `GET /api/settings/`

**Response:**
```json
{
  "user_id": "user123",
  "language": "en",
  "appearance": "system",
  "notifications": {
    "enabled": true,
    "consultation_notifications": true,
    "prescription_notifications": true,
    "lab_result_notifications": true,
    "appointment_notifications": true,
    "vital_alerts": true,
    "medication_reminders": true,
    "general_notifications": true,
    "quiet_hours_enabled": false,
    "quiet_hours_start": null,
    "quiet_hours_end": null
  },
  "sync": {
    "auto_sync_enabled": true,
    "sync_on_wifi_only": false,
    "sync_frequency": "realtime",
    "sync_health_records": true,
    "sync_prescriptions": true,
    "sync_lab_reports": true,
    "sync_vital_data": true
  },
  "privacy": {
    "share_data_for_research": false,
    "allow_analytics": true,
    "allow_crash_reporting": true,
    "data_retention_days": 365
  },
  "storage": {
    "used_mb": 245.5,
    "total_mb": 500.0,
    "usage_percentage": 49.1,
    "breakdown": {
      "health_records": 12.5,
      "vital_data": 2.3,
      "media": 220.0,
      "cache": 10.0
    },
    "last_cleared": "2024-01-15T10:30:00Z"
  },
  "security": {
    "encryption_enabled": true,
    "encryption_algorithm": "AES-256-GCM",
    "tls_version": "TLS 1.3",
    "two_factor_enabled": false,
    "last_password_change": "2024-01-01T00:00:00Z",
    "account_created": "2023-12-01T00:00:00Z",
    "last_login": "2024-01-20T08:15:00Z",
    "active_sessions": 1
  },
  "created_at": "2023-12-01T00:00:00Z",
  "updated_at": "2024-01-20T08:15:00Z"
}
```

---

## Update Settings

Update user settings (language, appearance, notifications, sync, privacy).

**Endpoint:** `PUT /api/settings/`

**Request Body:**
```json
{
  "language": "hi",  // Optional: "en" | "hi" | "ta" | "te" | "bn"
  "appearance": "dark",  // Optional: "system" | "light" | "dark"
  "notifications": {  // Optional
    "enabled": true,
    "consultation_notifications": true,
    "prescription_notifications": false,
    "lab_result_notifications": true,
    "appointment_notifications": true,
    "vital_alerts": true,
    "medication_reminders": true,
    "general_notifications": false,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00"
  },
  "sync": {  // Optional
    "auto_sync_enabled": true,
    "sync_on_wifi_only": true,
    "sync_frequency": "hourly",  // "realtime" | "hourly" | "daily" | "manual"
    "sync_health_records": true,
    "sync_prescriptions": true,
    "sync_lab_reports": true,
    "sync_vital_data": true
  },
  "privacy": {  // Optional
    "share_data_for_research": false,
    "allow_analytics": true,
    "allow_crash_reporting": true,
    "data_retention_days": 365
  }
}
```

**Response:** Same as GET /api/settings/

---

## Get Storage Info

Get offline storage usage information.

**Endpoint:** `GET /api/settings/storage`

**Response:**
```json
{
  "used_mb": 245.5,
  "total_mb": 500.0,
  "usage_percentage": 49.1,
  "breakdown": {
    "health_records": 12.5,
    "vital_data": 2.3,
    "media": 220.0,
    "cache": 10.0
  },
  "last_cleared": "2024-01-15T10:30:00Z"
}
```

---

## Clear Storage

Clear offline storage (cache, records, media).

**Endpoint:** `POST /api/settings/storage/clear`

**Request Body:**
```json
{
  "clear_cache": true,
  "clear_offline_records": false,
  "clear_media": false,
  "clear_all": false  // If true, clears everything
}
```

**Response:**
```json
{
  "cleared_mb": 10.5,
  "remaining_mb": 235.0,
  "cleared_at": "2024-01-20T10:30:00Z"
}
```

---

## Get Notification Preferences

Get notification preferences.

**Endpoint:** `GET /api/settings/notifications`

**Response:**
```json
{
  "enabled": true,
  "consultation_notifications": true,
  "prescription_notifications": true,
  "lab_result_notifications": true,
  "appointment_notifications": true,
  "vital_alerts": true,
  "medication_reminders": true,
  "general_notifications": true,
  "quiet_hours_enabled": false,
  "quiet_hours_start": null,
  "quiet_hours_end": null
}
```

---

## Update Notification Preferences

Update notification preferences.

**Endpoint:** `PUT /api/settings/notifications`

**Request Body:**
```json
{
  "enabled": true,
  "consultation_notifications": true,
  "prescription_notifications": false,
  "lab_result_notifications": true,
  "appointment_notifications": true,
  "vital_alerts": true,
  "medication_reminders": true,
  "general_notifications": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00"
}
```

**Response:** Updated notification preferences

---

## Get Security Info

Get security information (encryption, TLS, 2FA, etc.).

**Endpoint:** `GET /api/settings/security`

**Response:**
```json
{
  "encryption_enabled": true,
  "encryption_algorithm": "AES-256-GCM",
  "tls_version": "TLS 1.3",
  "two_factor_enabled": false,
  "last_password_change": "2024-01-01T00:00:00Z",
  "account_created": "2023-12-01T00:00:00Z",
  "last_login": "2024-01-20T08:15:00Z",
  "active_sessions": 1
}
```

---

## Update Language

Update user language preference.

**Endpoint:** `PUT /api/settings/language`

**Request Body:**
```json
{
  "language": "hi"  // "en" | "hi" | "ta" | "te" | "bn"
}
```

**Response:**
```json
{
  "message": "Language updated successfully",
  "language": "hi"
}
```

---

## Update Appearance

Update appearance/theme preference.

**Endpoint:** `PUT /api/settings/appearance`

**Request Body:**
```json
{
  "appearance": "dark"  // "system" | "light" | "dark"
}
```

**Response:**
```json
{
  "message": "Appearance updated successfully",
  "appearance": "dark"
}
```

---

## Frontend Integration Examples

### React/TypeScript Example

```typescript
// Get all settings
const getSettings = async () => {
  const response = await fetch('/api/settings/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Update language
const updateLanguage = async (language: string) => {
  const response = await fetch('/api/settings/language', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ language })
  });
  return await response.json();
};

// Update appearance
const updateAppearance = async (appearance: string) => {
  const response = await fetch('/api/settings/appearance', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ appearance })
  });
  return await response.json();
};

// Get storage info
const getStorageInfo = async () => {
  const response = await fetch('/api/settings/storage', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Clear storage
const clearStorage = async (options: {
  clear_cache?: boolean;
  clear_offline_records?: boolean;
  clear_media?: boolean;
  clear_all?: boolean;
}) => {
  const response = await fetch('/api/settings/storage/clear', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(options)
  });
  return await response.json();
};

// Update notifications
const updateNotifications = async (preferences: NotificationPreferences) => {
  const response = await fetch('/api/settings/notifications', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(preferences)
  });
  return await response.json();
};
```

---

## Error Responses

All endpoints may return the following error responses:

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to [operation]"
}
```

---

## Notes

1. **Default Settings**: Settings are automatically created with defaults when a user first accesses settings.

2. **Storage Calculation**: Storage usage is calculated based on:
   - Health records: ~50KB per record
   - Vital data: ~1KB per data point
   - Media files: Estimated from attachments
   - Cache: Base 10MB

3. **Language Codes**: Supported languages:
   - `en`: English
   - `hi`: Hindi (हिंदी)
   - `ta`: Tamil (தமிழ்)
   - `te`: Telugu (తెలుగు)
   - `bn`: Bengali (বাংলা)

4. **Appearance Modes**:
   - `system`: Follow system theme
   - `light`: Light theme
   - `dark`: Dark theme

5. **Sync Frequencies**:
   - `realtime`: Sync immediately
   - `hourly`: Sync every hour
   - `daily`: Sync once per day
   - `manual`: Sync only when manually triggered

