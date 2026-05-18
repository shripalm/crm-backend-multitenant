# crm-backend-multitenant

## Multi-Tenant CRM Backend with FastAPI

This repository hosts the backend for a multi-tenant Customer Relationship Management (CRM) system. Developed in Python using the FastAPI framework, it provides a robust and scalable API for managing various CRM functionalities, including user authentication, lead management, project tracking, billing, and reporting, all designed to support multiple independent tenants.

## Overview

The `crm-backend-multitenant` project is a comprehensive backend solution for a CRM application. It is built with a focus on high performance, scalability, and maintainability, leveraging modern Python asynchronous capabilities. The multi-tenant architecture ensures data isolation and customizable experiences for different organizations or clients using the CRM. It includes a wide array of modules covering core CRM operations, administrative tasks, agent-specific functionalities, and robust reporting.

## Features

*   **Multi-Tenancy**: Designed from the ground up to support multiple independent tenants with isolated data.
*   **Robust Authentication & Authorization**: Secure user, agent, and admin authentication using JWT, bcrypt for password hashing, and role-based access control (RBAC) with granular permissions.
*   **Comprehensive CRM Modules**:
    *   **Lead Management**: Create, track, and manage leads through various stages.
    *   **Contact Management**: Store and organize customer and prospect contact information.
    *   **Project Management**: Track projects, tasks, and associated activities.
    *   **Booking & Site Visit Management**: Schedule and manage customer bookings and site visits.
    *   **Task Management**: Assign, track, and manage tasks for users and agents.
    *   **Ticket System**: Handle customer support tickets with status tracking and history.
*   **Billing & Payments**: Integrated modules for managing billing records, invoices, subscriptions, and payment processing (including Paytm integration).
*   **Reporting & Analytics**: Generate various reports on leads, sales, call activities, and overall CRM performance. Data processing capabilities with Pandas and OpenPyXL.
*   **Email Notifications**: Integration with SendGrid for sending transactional emails and notifications.
*   **File Uploads**: Support for uploading and managing files, potentially integrated with cloud storage (e.g., AWS S3 via Boto3).
*   **Health Monitoring**: Dedicated health endpoints for system status checks.
*   **Developer Settings**: Endpoints for database migration, version checks, and schema management.
*   **Logging & Error Handling**: Structured logging with `structlog` and comprehensive error handling.

## Tech Stack

*   **Language**: Python
*   **Web Framework**: FastAPI
*   **Asynchronous Server**: Uvicorn
*   **Database**: PostgreSQL (inferred from SQLAlchemy, asyncpg, Alembic)
*   **ORM**: SQLAlchemy 2.0+
*   **Database Migrations**: Alembic
*   **Data Validation**: Pydantic 2.0+
*   **Environment Management**: python-dotenv, pydantic-settings
*   **Authentication**: PyJWT, Passlib (bcrypt)
*   **HTTP Client**: httpx, requests
*   **Testing**: pytest, pytest-asyncio
*   **Data Processing**: pandas, openpyxl, numpy, scipy
*   **Cloud Integration**: boto3, botocore (for AWS services like S3)
*   **Email**: email-validator, sendgrid
*   **Payment Gateway**: paytmchecksum, Crypto
*   **Logging**: structlog
*   **Debugging**: debugpy
*   **Video Processing (Optional/Utility)**: opencv-python-headless, yt-dlp (Note: These are present in dependencies and might be used for specific media-related features not typical for a core CRM, but included for completeness.)

## Installation

### Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3.9+
*   pip (Python package installer)
*   Docker and Docker Compose (recommended for local development and database setup)
*   A PostgreSQL database instance (can be run via Docker)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shripalm/crm-backend-multitenant.git
    cd crm-backend-multitenant
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of the project based on the `.env.example` (if available) or the `Environment Variables` section below.

5.  **Database Setup (using Docker Compose for PostgreSQL):**
    If you're using Docker Compose for your database, you can start it:
    ```bash
    docker-compose up -d postgres
    ```
    Ensure your `DATABASE_URL` in `.env` points to this instance.

6.  **Run Database Migrations:**
    Initialize and apply database migrations using Alembic.
    ```bash
    # Ensure alembic.ini is configured correctly
    alembic upgrade head
    ```

7.  **Start the Application:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API documentation (Swagger UI) will be available at `http://127.0.0.1:8000/docs`.

## Environment Variables

The application relies on the following environment variables, typically defined in a `.env` file:

*   `DATABASE_URL`: The connection string for your PostgreSQL database (e.g., `postgresql+asyncpg://user:password@host:port/dbname`).
*   `ENV_FILE`: Path to the environment file (often `.env` itself, or used for different environments).
*   `SECRET_KEY`: A strong, random string used for JWT token signing.
*   `ALGORITHM`: The algorithm used for JWT signing (e.g., `HS256`).
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens in minutes.
*   `REFRESH_TOKEN_EXPIRE_DAYS`: Expiration time for refresh tokens in days.
*   `ADMIN_EMAIL`: Default admin email for initial setup.
*   `ADMIN_PASSWORD`: Default admin password for initial setup.
*   `SENDGRID_API_KEY`: API key for SendGrid email service.
*   `PAYTM_MERCHANT_KEY`: Merchant key for Paytm integration.
*   `PAYTM_MERCHANT_ID`: Merchant ID for Paytm integration.
*   `AWS_ACCESS_KEY_ID`: AWS access key for S3 integration.
*   `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 integration.
*   `AWS_REGION_NAME`: AWS region for S3.
*   `AWS_BUCKET_NAME`: S3 bucket name for file uploads.

*(Note: This list is illustrative; refer to `app/core/config.py` or similar for the exact required variables.)*

## API Endpoints

The API is structured versioned (`/api/v1`) and organized by functional areas. Full interactive documentation is available via Swagger UI at `/docs` when the application is running.

Here's a glimpse of the main endpoint categories:

*   `/api/v1/health`: Basic health check endpoint.
*   `/api/v1/auth`: User authentication (login, register, password reset).
*   `/api/v1/admin/auth`: Admin-specific authentication.
*   `/api/v1/agents/auth`: Agent-specific authentication.
*   `/api/v1/leads`: Lead creation, retrieval, update, and deletion.
*   `/api/v1/contacts`: Contact management.
*   `/api/v1/projects`: Project creation and management.
*   `/api/v1/bookings`: Booking scheduling and management.
*   `/api/v1/site-visit`: Site visit scheduling and tracking.
*   `/api/v1/tasks`: Task assignment and status updates.
*   `/api/v1/tickets`: Customer support ticket system.
*   `/api/v1/payments`: Payment processing and records.
*   `/api/v1/admin/billing`: Admin-level billing management.
*   `/api/v1/reports`: Various CRM reports and analytics.
*   `/api/v1/permissions`: Role and permission management.
*   `/api/v1/upload`: File upload functionality.
*   `/api/settings/db_migrate`: Database migration endpoint (for development/admin use).
*   `/api/settings/db_version_check`: Check current database version.

## Folder Structure

The project follows a modular structure to ensure clear separation of concerns:

```
.
├── app/
│   ├── api/                  # API endpoints and routers
│   │   ├── v1/               # Version 1 of the API
│   │   │   └── routers/      # Individual router modules for each feature
│   ├── core/                 # Core configurations, security, and utilities
│   ├── db/                   # Database connection, session management, models base
│   ├── enums/                # Enumerations for various states and types
│   ├── middleware/           # FastAPI middleware components
│   ├── models/               # SQLAlchemy ORM models for database tables
│   ├── repositories/         # Data access layer
│   ├── schemas/              # Pydantic schemas for request/response validation
│   ├── services/             # Business logic and service layer
│   ├── utils/                # Helper functions and utilities
│   └── main.py               # Main FastAPI application entry point
├── scripts/                  # Placeholder for utility scripts
├── Dockerfile                # Docker build instructions
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Python dependencies
└── .env.example              # Example environment variables
```

## Scripts

While no specific executable scripts were detected in the `scripts/` directory, common operations include:

*   **Database Migrations**: Handled via `alembic` commands (e.g., `alembic revision --autogenerate -m "Add new table"`, `alembic upgrade head`).
*   **Running Tests**: `pytest` to execute unit and integration tests.
*   **Linting/Formatting**: Tools like `black` or `isort` for code quality.

## Deployment

The project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

1.  **Build Docker Image:**
    ```bash
    docker build -t crm-backend-multitenant .
    ```

2.  **Run with Docker Compose:**
    The `docker-compose.yml` can be used to orchestrate the application along with its database.
    ```bash
    docker-compose up --build -d
    ```
    This will build the image (if not already built) and start the application and its dependencies in detached mode.

## Future Improvements

*   **Comprehensive Testing**: Expand unit and integration test coverage.
*   **CI/CD Pipeline**: Implement a robust CI/CD pipeline for automated testing and deployment.
*   **Real-time Features**: Integrate WebSockets for real-time updates (e.g., ticket status, chat).
*   **Advanced Analytics**: Integrate with dedicated analytics platforms or implement more complex data processing pipelines.
*   **Caching**: Implement caching strategies (e.g., Redis) to improve performance for frequently accessed data.
*   **Observability**: Enhance monitoring, logging, and tracing capabilities.
*   **Scalability**: Explore Kubernetes deployment for advanced orchestration and scaling.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.