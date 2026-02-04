# GP Secure System

A Django-based secure management system for general practice (GP) operations, including patient records, appointments, audits, and account management.

## Project Overview

This is a full-stack application built with Django REST Framework and PostgreSQL, containerized with Docker for easy deployment. The system manages multiple user roles (GP, patient, receptionist, manager) with secure audit logging and appointment management.

## Features

- **User Management**: Account management for different user roles (GP, patient, receptionist, manager)
- **Appointments**: Schedule and manage GP appointments with availability tracking
- **Patient Records**: Secure storage and retrieval of patient health records
- **Audit Logging**: Comprehensive audit trail for all system operations
- **REST API**: Full REST API with JWT authentication
- **Multi-role Frontend**: Role-specific interfaces for different user types

## Technology Stack

- **Backend**: Django 5.2.10 with Django REST Framework
- **Database**: PostgreSQL 16
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML/CSS/JavaScript

## Project Structure

```
gp-secure-system/
├── backend/                    # Django application
│   ├── accounts/              # User account management
│   ├── appointments/          # Appointment scheduling
│   ├── audits/                # Audit logging system
│   ├── records/               # Patient medical records
│   ├── config/                # Django configuration
│   ├── frontend/              # HTML/CSS/JS frontend files
│   ├── manage.py              # Django management script
│   ├── requirements.txt        # Backend dependencies
│   └── Dockerfile             # Backend container config
├── db/
│   └── init/                  # Database initialization scripts
├── docker-compose.yml         # Container orchestration
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

## Available URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/` | Main application |
| `http://localhost:8000/admin/` | Django admin panel |
| `http://localhost:8000/api/schema/swagger/` | Swagger API documentation |
| `http://localhost:8000/gp.html` | GP interface |
| `http://localhost:8000/patient.html` | Patient interface |
| `http://localhost:8000/receptionist.html` | Receptionist interface |
| `http://localhost:8000/manager.html` | Manager interface |

## API Endpoints

API endpoints are organized by app:

- **Accounts**: `/api/accounts/` - User authentication and profile management
- **Appointments**: `/api/appointments/` - Appointment scheduling
- **Records**: `/api/records/` - Patient medical records
- **Audits**: `/api/audits/` - Audit log retrieval

For detailed API documentation, visit the Swagger UI at `/api/schema/swagger/`

## Management Commands

```bash
cd backend

# Create initial data (if seed script exists)
python manage.py shell < /app/seed_users.py

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

## Database

PostgreSQL 16 is used with pgcrypto extension enabled for secure password hashing.

**Default credentials** (for development):
- Database: `gpdb`
- User: `gpuser`
- Password: `gppassword`
- Port: `5432`

⚠️ **Important**: Change these credentials in production!

## Environment Variables

Create a `.env` file in the project root with:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=0  # Set to 1 for development
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

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

## Security Notes

- Never commit `.env` file with sensitive credentials
- Change `DJANGO_SECRET_KEY` in production
- Set `DJANGO_DEBUG=0` in production
- Use strong database passwords
- Enable HTTPS in production
- Regularly review audit logs

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure nothing breaks
4. Submit a pull request

## Support

For issues or questions, check the project documentation or contact the development team.


