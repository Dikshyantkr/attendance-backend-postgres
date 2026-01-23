# Attendance System Backend (FastAPI)

## Overview
A backend-focused attendance system built to learn and demonstrate
industry-level authentication, authorization, and database practices.

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic (migrations)
- JWT Authentication
- Passlib (bcrypt)

## Features
- User management
- Secure login with JWT
- Password hashing
- Role-Based Access Control (Admin / Employee)
- Protected attendance check-in / check-out APIs
- Environment-based configuration
- Versioned database schema with Alembic

## Authentication Flow
1. User logs in via `/auth/login`
2. Server returns JWT access token
3. Token is passed via `Authorization: Bearer <token>`
4. Protected routes validate token and role

## Roles
- **Employee**
  - Check-in / Check-out
  - Access own attendance only
- **Admin**
  - View all users
  - View all attendance records

## Running Locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

