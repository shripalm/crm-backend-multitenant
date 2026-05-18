# CRM Backend

A modern, multi-tenant CRM (Customer Relationship Management) backend API built with **FastAPI** and **PostgreSQL**. This project provides comprehensive features for managing users, projects, contacts, leads, bookings, payments, and more.

## 🚀 Features

- **Multi-tenant Architecture**: Support for multiple clients with isolated data
- **Authentication & Authorization**: User, Admin, and Agent authentication with role-based access control
- **User Management**: User profiles, roles, permissions, and OTP-based authentication
- **CRM Core Features**:
  - Projects and Properties management
  - Contacts and Leads tracking
  - Call Reports and Site Visits
  - Task Management
  - Booking System
- **Billing & Payments**: 
  - Subscription management
  - Payment processing with Paytm integration
  - Billing records tracking
- **Ticket Management**: Admin and Agent ticket systems with history tracking
- **File Uploads**: CSV/Excel file upload and processing
- **Real-time Logging**: Structured logging with context-aware information
- **RESTful API**: Comprehensive API endpoints for all operations
- **Docker Support**: Ready for containerized deployment

## 🛠 Tech Stack

- **Framework**: FastAPI >= 0.95.0
- **Server**: Uvicorn
- **DB ORM**: SQLAlchemy >= 2.0
- **Database**: PostgreSQL (asyncpg)
- **Migrations**: Alembic
- **Authentication**: JWT, Passlib with bcrypt
- **Validation**: Pydantic >= 2.0
- **File Processing**: Pandas, OpenPyXL
- **Payment**: Paytm integration
- **AWS**: S3 file uploads (boto3)
- **Email**: SendGrid integration
- **Testing**: pytest, pytest-asyncio

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Docker & Docker Compose (for containerized deployment)
- pip or virtual environment manager

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/crm_db
ADMIN_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/admin_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1

# SendGrid
SENDGRID_API_KEY=your-sendgrid-key

# Stage
STAGE_PATH=/api/v1
PROJECT_NAME=CRM-Backend
```

### 5. Initialize the database
```bash
# Run migrations
alembic upgrade head

# For admin database
alembic -c admin_alembic.ini upgrade head
```

## 🐳 Docker Setup

### Using Docker Compose
```bash
docker-compose up --build
```

The application will be available at `http://localhost:80`

### Manual Docker build
```bash
docker build -t crm-backend .
docker run -p 80:80 --env-file .env crm-backend
```

## 🚀 Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 80 --workers 4
```

## 📁 Project Structure

```
.
├── alembic/                 # Database migrations
│   └── versions/           # Migration files
├── admin_alembic/          # Admin database migrations
│   └── versions/
├── app/                    # Main application code
│   ├── api/               # API routes and endpoints
│   │   └── v1/routers/   # Route handlers (auth, users, projects, etc.)
│   ├── core/             # Core configuration
│   ├── db/               # Database models and setup
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Database access layer
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic
│   ├── middleware/       # Custom middleware (auth, logging, client headers)
│   ├── enums/            # Enum definitions
│   ├── utils/            # Utility functions and helpers
│   └── main.py          # FastAPI application entry point
├── scripts/              # Utility scripts for maintenance
│   ├── admin_db.sh
│   ├── create_admin_db.py
│   ├── migrate_all_clients.py
│   └── ...
├── tests/               # Test suite
│   ├── db/             # Database tests
│   └── services/       # Service tests
├── documentation/      # Project documentation
├── requirements.txt    # Python dependencies
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile         # Docker image specification
└── pytest.ini        # Pytest configuration
```

## 🔌 API Endpoints

The API is organized into several modules:

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/admin/auth/login` - Admin login
- `POST /api/v1/agents/auth/login` - Agent login

### Users & Access Control
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Projects & Properties
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/properties` - List properties

### CRM Features
- `GET /api/v1/contacts` - List contacts
- `POST /api/v1/leads` - Create lead
- `GET /api/v1/bookings` - List bookings
- `POST /api/v1/call-reports` - Create call report

### Billing & Payments
- `GET /api/v1/admin/billing` - Billing information
- `POST /api/v1/payments` - Process payment

### Tickets
- `GET /api/v1/tickets` - List tickets
- `POST /api/v1/tickets` - Create ticket

For complete API documentation, run the application and visit `/docs` for interactive Swagger UI.

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test
```bash
pytest tests/services/test_auth.py
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

### Test Configuration
Tests are configured in `pytest.ini` and use fixtures defined in `tests/conftest.py`

## 🗄️ Database Management

### Create a Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic current
alembic history
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt-based password encryption
- **OTP Verification**: One-Time Password for enhanced security
- **Role-Based Access Control**: Fine-grained permission management
- **Client Middleware**: Multi-tenant data isolation
- **Request Validation**: Pydantic schema validation
- **CORS**: Configurable cross-origin requests

## 📊 Monitoring & Logging

The application uses structured logging with context information:

```python
logger.info("Event description", user_id=123, action="login")
```

Logs include:
- Request details
- User information
- Database operations
- Error traces

## 📦 Dependencies Management

Key dependencies:
- FastAPI: Web framework
- SQLAlchemy: ORM
- Asyncpg: PostgreSQL async driver
- Pydantic: Data validation
- Alembic: Database migrations
- Boto3: AWS S3 integration
- Requests: HTTP client
- Sendgrid: Email service

## 🚢 Deployment

### Docker Hub
```bash
docker build -t your-registry/crm-backend:latest .
docker push your-registry/crm-backend:latest
```

### Environment Variables
Ensure these are set in your deployment environment:
- `DATABASE_URL`
- `ADMIN_DATABASE_URL`
- `SECRET_KEY`
- `AWS_*` credentials
- `SENDGRID_API_KEY`

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "Add your feature"`
3. Push branch: `git push origin feature/your-feature`
4. Submit a Pull Request

## 📝 API Response Format

All responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database user has correct permissions

### Migration Errors
```bash
# Check current migration status
alembic current

# View all migrations
alembic history

# Reset to specific version
alembic downgrade <revision>
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation

- [Database Documentation](documentation/db-doc.md)
- [Setup Instructions](scripts/README.md)

## 👥 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## 🔗 Related

- API runs on port `80` (production) or `8000` (development)
- Admin panel typically served on a separate frontend application
- Database migrations are automatically tracked

---

**Last Updated**: May 2026
**API Version**: v1
**Python Version**: 3.12+
