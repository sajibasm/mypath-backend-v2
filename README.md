## Django REST Framework Complete Authentication API 

## To Run this Project follow below:

## Setup Instructions

To run this project, follow these steps: <br>
### 1. Create a Virtual Environment
Creating a virtual environment helps to manage dependencies for your project. Run the following command to create a virtual environment named authenv:

    python3 -m venv venv

### 2. Activate the Virtual Environment
activate the newly created virtual environment <br> 

    source venv/bin/activate

### 3. Update the Pip<br/>

    python3 -m pip install --upgrade pip

### 3. Install Required Packages <br/>
Once the virtual environment is activated, install the necessary packages listed in requirements.txt: <br>

    pip install -r requirements.txt

### 4. Apply Migrations
Before running the server, apply the migrations to set up your database schema: <br>

    python3 manage.py makemigrations
    
    python3 manage.py showmigrations
    
    python3 manage.py migrate
    

### 5. Create a Superuser (Optional)
To create superuser <br>

    python3 manage.py createsuperuser

### 6. Run the Development Server
Start the Django development server to serve your application: <br>

    python3 manage.py runserver


### Running in Production
To run Django and Celery simultaneously in production, follow the steps below:
## 1. Use Gunicorn instead of runserver
gunicorn rootApp.wsgi:application --bind 0.0.0.0:9000 --workers 3

## 2. Run Celery Worker <br>
celery -A rootApp worker --loglevel=info

## 3. Use Supervisor to Manage Both Processes

sudo apt install supervisor


### Requirements
Ensure you have the following packages installed, as listed in requirements.txt: <br/>

celery -A rootApp.celery_app worker --loglevel=info