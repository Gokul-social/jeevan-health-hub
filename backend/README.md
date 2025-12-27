# Jeevan+ Telemedicine Backend

Production-ready, offline-first telemedicine backend for rural healthcare application.

## 🏗️ Architecture

- **Framework**: FastAPI (Python 3.11+)
- **Database**: Firestore (NoSQL, offline-first)
- **Storage**: Firebase Storage (medical images, reports)
- **Authentication**: JWT with RBAC
- **Security**: AES-256 field-level encryption
- **Deployment**: Docker + Google Cloud Run

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration and security
│   │   ├── config.py          # Settings management
│   │   ├── security.py        # JWT, RBAC, password hashing
│   │   ├── encryption.py      # Field-level encryption
│   │   └── dependencies.py    # Shared dependencies
│   ├── auth/                   # Authentication module
│   │   ├── routes.py          # Auth endpoints
│   │   ├── service.py         # Auth business logic
│   │   └── schemas.py         # Auth Pydantic models
│   ├── users/                  # User management
│   ├── records/                # Health records (offline-first)
│   ├── ai/                     # AI symptom checker
│   ├── consultation/           # Telemedicine consultations
│   ├── pharmacy/               # Pharmacy & medicine availability
│   ├── iot/                    # IoT vital data collection
│   └── utils/                  # Utility functions
├── tests/                      # Test suite
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Local development setup
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized setup)
- Firebase project with Firestore enabled
- Firebase service account credentials

### Local Development

1. **Clone and setup**:
```bash
cd backend
cp .env.example .env
# Edit .env with your Firebase credentials
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run with Docker Compose** (includes Firestore emulator):
```bash
docker-compose up
```

4. **Or run directly**:
```bash
uvicorn app.main:app --reload --port 8080
```

5. **Access API docs**:
- Swagger UI: http://localhost:8080/api/docs
- ReDoc: http://localhost:8080/api/redoc

## 🔐 Authentication

### Register User
```bash
POST /api/auth/register
{
  "phone": "+1234567890",
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "role": "patient"
}
```

### Login
```bash
POST /api/auth/login
{
  "phone": "+1234567890",
  "password": "securepassword"
}

# Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Use Token
```bash
Authorization: Bearer <access_token>
```

## 📡 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get tokens
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user profile

### Users (`/api/users`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile
- `POST /family/link` - Link family member
- `PUT /doctor/profile` - Update doctor profile
- `POST /doctor/{id}/verify` - Verify doctor (admin)

### Health Records (`/api/records`)
- `POST /medical-history` - Create medical history
- `POST /prescription` - Create prescription
- `POST /lab-report` - Create lab report
- `GET /` - List records (paginated)
- `GET /{id}` - Get record
- `PUT /{id}` - Update record
- `DELETE /{id}` - Delete record
- `POST /resolve-conflict` - Resolve sync conflict
- `GET /sync/pending` - Get pending sync records

### AI Services (`/api/ai`)
- `POST /symptom-check` - Analyze symptoms

### Consultations (`/api/consultations`)
- `POST /` - Create consultation
- `GET /{id}` - Get consultation
- `POST /{id}/join` - Join consultation
- `POST /{id}/end` - End consultation
- `POST /{id}/signal` - Send WebRTC signal
- `GET /{id}/signals` - Get pending signals

### Pharmacy (`/api/pharmacy`)
- `POST /` - Create pharmacy (admin)
- `GET /{id}` - Get pharmacy
- `PUT /{id}/stock` - Update medicine stock
- `POST /search` - Search medicine availability
- `GET /alerts/low-stock` - Get low stock alerts

### IoT (`/api/iot`)
- `POST /data/batch` - Store vital data batch
- `GET /data/recent` - Get recent vitals
- `POST /data/timeseries` - Get time-series data
- `GET /alerts` - Get active alerts

## 🔒 Security Features

1. **JWT Authentication**
   - Short-lived access tokens (30 min)
   - Long-lived refresh tokens (7 days)
   - Token validation middleware

2. **Role-Based Access Control (RBAC)**
   - Roles: `patient`, `doctor`, `admin`
   - Route-level permission checks

3. **Field-Level Encryption**
   - AES-256-GCM encryption
   - Encrypted fields: phone, email, license numbers
   - Automatic encryption/decryption

4. **Rate Limiting**
   - Configurable per-minute limits
   - Per-user/IP tracking

5. **Input Validation**
   - Pydantic v2 models
   - Request validation
   - SQL injection prevention (NoSQL)

## 📊 Offline-First Design

Health records support offline-first operation:

1. **Versioning**: Each record has a version number
2. **Conflict Detection**: Server detects version conflicts
3. **Conflict Resolution**: Client can resolve conflicts
4. **Sync Status**: Track pending/synced records
5. **Audit Trail**: Immutable audit logs

### Conflict Resolution Flow

```python
# Client sends record with version
POST /api/records/medical-history
{
  "title": "Fever",
  "client_version": 5
}

# If conflict (409):
{
  "message": "Version conflict",
  "server_version": 6,
  "client_version": 5,
  "server_data": {...}
}

# Resolve conflict:
POST /api/records/resolve-conflict
{
  "record_id": "...",
  "chosen_version": 6,
  "resolved_data": {...}
}
```

## 🤖 AI Symptom Checker

Supports multiple AI backends:

1. **Local Rule-Based** (default)
   - Pattern matching
   - Symptom-condition mapping
   - No external dependencies

2. **HuggingFace** (optional)
   - ML model inference
   - Requires API key

3. **Google Gemini** (optional)
   - LLM-based analysis
   - Requires API key

4. **Automatic Fallback**
   - Falls back to local if cloud fails

## 🏥 Consultation System

- **Session Management**: Create, join, end consultations
- **WebRTC Signaling**: Offer/answer/ICE candidate exchange
- **Session Tokens**: Encrypted tokens for security
- **Multiple Types**: Video, audio, text consultations

## 💊 Pharmacy System

- **Pharmacy Management**: CRUD operations
- **Stock Tracking**: Real-time medicine availability
- **Location-Based Search**: Find nearby pharmacies
- **Low Stock Alerts**: Automatic alerts when stock is low

## 📱 IoT Integration

- **Device Authentication**: Token-based device auth
- **Batch Data Collection**: Efficient bulk uploads
- **Time-Series Storage**: Historical vital data
- **Alert Generation**: Automatic threshold-based alerts
- **Metrics**: Heart rate, BP, SpO2, temperature, glucose, weight

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t jeevan-backend .
```

### Run Container
```bash
docker run -p 8080:8080 \
  -e FIREBASE_PROJECT_ID=your-project \
  -e SECRET_KEY=your-secret \
  jeevan-backend
```

## ☁️ Google Cloud Run Deployment

1. **Build and push**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/jeevan-backend
```

2. **Deploy**:
```bash
gcloud run deploy jeevan-backend \
  --image gcr.io/PROJECT_ID/jeevan-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=your-project
```

3. **Set secrets** (recommended):
```bash
gcloud secrets create secret-key --data-file=secret.txt
gcloud run services update jeevan-backend \
  --update-secrets SECRET_KEY=secret-key:latest
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

## 📝 Environment Variables

See `.env.example` for all configuration options.

**Required**:
- `SECRET_KEY` - JWT signing key
- `ENCRYPTION_KEY` - AES encryption key
- `FIREBASE_PROJECT_ID` - Firebase project ID

**Optional**:
- `FIREBASE_CREDENTIALS_PATH` - Service account JSON path
- `AI_SERVICE_TYPE` - AI backend (local/huggingface/gemini)
- `WEBRTC_TURN_SERVER` - TURN server for WebRTC

## 🔧 Development

### Code Style
```bash
black app/
flake8 app/
mypy app/
```

### Project Structure Guidelines
- **Routes**: HTTP endpoints, request/response handling
- **Services**: Business logic, database operations
- **Schemas**: Pydantic models for validation
- **Core**: Shared utilities, security, config

## 📄 License

Proprietary - Jeevan+ Telemedicine Platform

## 🤝 Contributing

This is a production codebase. All changes must:
1. Pass all tests
2. Follow code style guidelines
3. Include security review
4. Update documentation

## 🆘 Support

For issues or questions, contact the development team.

---

**Built with ❤️ for rural healthcare**

