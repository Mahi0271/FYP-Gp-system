# GP Secure System

A Django-based secure management system for general practice (GP) operations, including patient records, appointments, audits, and account management.

## Project Overview

This is a full-stack application built with Django REST Framework and PostgreSQL, containerized with Docker for easy deployment. The system manages multiple user roles (GP, patient, receptionist, manager) with secure audit logging and appointment management.

## Features

- **User Management**: Account management for different user roles (GP, patient, receptionist, practice manager) with role-based access control
- **Multi-Factor Authentication (MFA)**: TOTP-based MFA support for enhanced security
- **Patient Records**: Secure storage and retrieval of patient health records with encrypted clinical entries
- **Clinical Entries**: Support for notes, diagnoses, and prescriptions with encryption
- **Appointments**: Schedule and manage GP appointments with availability tracking and patient-GP assignment
- **Audit Logging**: Comprehensive audit trail for all system operations with user tracking
- **REST API**: Full REST API with JWT authentication and OpenAPI/Swagger documentation
- **Dashboard**: Analytics and quick-access dashboard for different user types
- **Multi-role Frontend**: Role-specific interfaces for GPs, patients, receptionists, and managers
- **Database Encryption**: Patient data encryption using pgcrypto with encrypted field support

## Technology Stack

- **Backend**: Django 5.2.10 with Django REST Framework 3.16
- **Database**: PostgreSQL 16 with pgcrypto extension for encryption
- **Authentication**: JWT with djangorestframework-simplejwt
- **Multi-Factor Authentication**: TOTP via pyotp
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML/CSS/JavaScript with role-based interfaces

## Project Structure

```
gp-secure-system/
├── backend/                    # Django application
│   ├── accounts/              # User account & authentication management
│   ├── appointments/          # Appointment scheduling & availability
│   ├── audits/                # Audit logging & compliance tracking
│   ├── records/               # Patient medical records with encryption
│   ├── dashboard/             # Analytics & dashboards
│   ├── config/                # Django configuration
│   ├── frontend/              # HTML/CSS/JS frontend files
│   ├── manage.py              # Django management script
│   ├── requirements.txt        # Backend dependencies
│   ├── Dockerfile             # Backend container config
│   └── migrations/            # Database migrations (per app)
├── db/
│   ├── init/                  # Database initialization scripts
│   │   └── 01-enable-pgcrypto.sql  # pgcrypto extension setup
│   └── db_data/               # Persistent database volume
├── docker-compose.yml         # Container orchestration
├── .env                       # Environment configuration (not in git)
├── .env.example               # Example environment template
├── requirements.txt           # Root dependencies
└── README.md                  # This file
```

## Prerequisites

- **Docker** and **Docker Compose** installed
- Or alternatively, Python 3.10+ and PostgreSQL 16+

## Installation & Setup

### Option 1: Using Docker (Recommended)

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd gp-secure-system
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env  # Create from example if available
   ```
   
   Or create a `.env` file with necessary variables:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=0
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. **Build and start containers**:
   ```bash
   docker compose up -d
   ```

4. **Access the application**:
   - Web Interface: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/api/schema/swagger/

### Option 2: Local Development Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

2. **Set up PostgreSQL database**:
   - Create database: `gpdb`
   - Create user: `gpuser` with password `gppassword`
   - Or modify settings in `backend/config/settings.py`

3. **Run migrations**:
   ```bash
   cd backend
   python manage.py migrate
   ```

4. **Create superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

## Running the Application

### With Docker
```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f web

# Stop services
docker compose down
```

### Locally
```bash
cd backend
python manage.py runserver
```

## ⚠️ Creating an Admin Account (REQUIRED)

**This step is crucial.** Without an admin account, you will not be able to create GP doctors, receptionists, or practice managers. Patient accounts can self-register, but all staff accounts must be created through the Django admin panel.

### Steps

1. **Ensure the containers are running**:
   ```bash
   docker compose up -d
   ```

2. **Open a shell inside the running web container**:
   ```bash
   docker exec -it gp_web bash
   ```

3. **Create the superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set a username, email, and password.

4. **Exit the container shell**:
   ```bash
   exit
   ```

5. **Log in to the admin panel** at `http://localhost:8000/admin/` using the credentials you just created.

6. **From the admin panel you can**:
   - Create GP doctor accounts (set role to `gp`)
   - Create receptionist accounts (set role to `receptionist`)
   - Create practice manager accounts (set role to `manager`)

> Without completing this step, the system will have no staff accounts and core functionality will be inaccessible.

---

## Available URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/` | Main application |
| `http://localhost:8000/admin/` | Django admin panel |
| `http://localhost:8000/api/schema/swagger/` | Swagger API documentation |
| `http://localhost:8000/gp.html` | GP/Doctor interface |
| `http://localhost:8000/patient.html` | Patient interface |
| `http://localhost:8000/receptionist.html` | Receptionist interface |
| `http://localhost:8000/manager.html` | Practice Manager interface |

## API Endpoints

API endpoints are organized by app:

- **Accounts**: `/api/accounts/` - User authentication, profile management, and MFA setup
- **Appointments**: `/api/appointments/` - Appointment scheduling and availability management
- **Records**: `/api/records/` - Patient medical records and clinical entries with encryption
- **Audits**: `/api/audits/` - Audit log retrieval and tracking
- **Dashboard**: `/api/dashboard/` - Analytics and statistics for different user roles

For detailed API documentation, visit the Swagger UI at `/api/schema/swagger/`

## Management Commands

```bash
cd backend

# Run migrations
python manage.py migrate

# Create superuser (admin user)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

### MFA/TOTP Setup

Users can enable Multi-Factor Authentication (MFA) through the API:
1. Call `/api/accounts/mfa/setup/` to generate a TOTP secret
2. Display QR code to user for scanning in authenticator app
3. User provides TOTP code to verify and enable MFA
4. User receives backup codes for account recovery

## Database

PostgreSQL 16 is used as the primary database with the pgcrypto extension enabled for secure encryption of sensitive fields.

**Default credentials** (for development only):
- Database: `gpdb`
- User: `gpuser`
- Password: `gppassword`
- Port: `5432`

**Important Database Features**:
- pgcrypto extension: Required for field-level encryption of clinical data
- Automatic initialization: pgcrypto is enabled via `db/init/01-enable-pgcrypto.sql` on first Docker Compose start

⚠️ **Important**: Change all database credentials in production!

## Environment Variables

Create a `.env` file in the project root with:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=0  # Set to 1 for development
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Configuration
POSTGRES_DB=gpdb
POSTGRES_USER=gpuser
POSTGRES_PASSWORD=gppassword
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Encryption Key (required for pgcrypto)
PGCRYPTO_KEY=your_encryption_key_here
```

⚠️ **Important**: The `PGCRYPTO_KEY` environment variable is **required** and must be set before running the application.

## Development

### Running Tests
```bash
cd backend
python manage.py test
```

### Making Database Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Django Admin
Access at `http://localhost:8000/admin/` with superuser credentials.

## Troubleshooting

### Port 8000 already in use
```bash
# Find and kill process using port 8000
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Database connection error
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure `docker compose up` completed successfully

### Migration errors
```bash
# Reset migrations (development only!)
python manage.py migrate accounts zero
python manage.py migrate
```

## Security Architecture

This system includes multiple security layers designed to protect sensitive healthcare data:

### Authentication & Authorization
- **JWT Authentication**: Token-based authentication using djangorestframework-simplejwt for secure API access
- **Multi-Factor Authentication (MFA)**: TOTP-based 2FA support for enhanced user account security
- **Role-Based Access Control**: Four user roles with specific permissions (Patient, GP, Receptionist, Practice Manager)

### Data Protection
- **Database Encryption**: Sensitive fields protected with PostgreSQL pgcrypto extension
- **Field-Level Encryption**: Clinical entries encrypted with `PGCRYPTO_KEY` for storage
- **Secure Passwords**: Django's PBKDF2 password hashing algorithm
- **Patient Data**: Comprehensive patient information with encrypted storage

### Audit & Compliance
- **Audit Logging**: Complete immutable audit trail of all system operations
- **User Attribution**: All actions tracked with user identification and timestamps
- **Access Tracking**: Appointment and record access logged for compliance

## Security Notes

- **Never commit** `.env` file with sensitive credentials to version control
- **Change `DJANGO_SECRET_KEY`** in production to a unique secure value
- **Set `DJANGO_DEBUG=0`** in production to disable debug mode
- **Use strong `PGCRYPTO_KEY`** for field-level encryption (required)
- **Use strong database passwords** different from defaults
- **Enable HTTPS** in production for encryption in transit
- **Regularly review audit logs** for suspicious activity
- **Change default credentials** from example values in .env.example
- **Keep dependencies updated** to receive security patches
- **Run security tests** before each production deployment

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure nothing breaks
4. Submit a pull request

## Support

For issues or questions, check the project documentation or contact the development team.


