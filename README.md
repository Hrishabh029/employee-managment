# Django Employee Management System

A simple and efficient employee management system built with Django.

## How to Run This Project

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Project
```bash
git clone https://github.com/Hrishabh029/Django-Project.git
cd Django-Project
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
.\venv\Scripts\activate
```

### Step 3: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Create Admin Account
```bash
python manage.py createsuperuser
# Enter your desired username, email, and password
```

### Step 6: Start the Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
1. Open your web browser
2. Go to: http://127.0.0.1:8000/admin
3. Login with your superuser credentials
4. Start using the system:
   - First add Departments
   - Then add Employees
   - Create Attendance records
   - Manage Leave requests
   - Process Payroll

## Features Available
- Employee Profile Management
- Department Management
- Attendance Tracking
- Leave Management
- Payroll Processing
- Document Management
- Performance Tracking

## Need Help?
If you encounter any issues:
1. Make sure all prerequisites are installed
2. Check if virtual environment is activated
3. Verify all requirements are installed correctly
4. Ensure database migrations are applied

## Contact
For any queries, reach out to me on GitHub: [@Hrishabh029](https://github.com/Hrishabh029)
