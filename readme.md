# Introduction

A simple project to manage invoices from different clients 
and take a look on some statistics.

Uses:

* Django 2.2.2
* SQLite
* Bootstrap 4

# How To

1. Install requirements
    ```bash
    python3 -m venv venv
    source venv/bin/activate.sh
    pip install -r requirements.txt
    ```

2. Run migrations

    ```bash
    python manage.py migrate
    ```

2. Create super user

    ```bash
    python manage.py createsuperuser
    ```

3. Start server

    ```bash
    python manage.py runserver
    ```
    
Now you can authorize as an superuser and manage your information.

To add Products and Clients you should open admin panel and add them there.

# ToDo's

* Add in stock products information
* Pack product into executables
* ...
