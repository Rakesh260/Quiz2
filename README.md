# Employee Data Management API

A Django REST Framework-based API for managing employee data including departments, attendance, performance, and leave records. The application is designed with modular architecture, throttling, authentication, and supports schema documentation.

## 🚀 Features

- RESTful API for Employee, Department, Attendance, Performance, and LeaveRecord
- JWT Authentication with DRF Simple JWT
- Rate throttling for users and anonymous requests
- Pagination support
- API schema generation and documentation using DRF’s `get_schema_view`
- PostgreSQL database integration
- Command to generate realistic test data

## 📦 Tech Stack

- Python 3.8
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- Faker (for data generation)

## 🛠 Setup Instructions
git clone <repo-url>
cd employee_project

python -m venv venv

source venv/bin/activate 

pip install -r requirements.txt (Install Dependencies)

python manage.py makemigrations(run migrations)

python manage.py migrate

python manage.py generate_fake_data(Generate Sample Data)

python manage.py runserver(start server)


