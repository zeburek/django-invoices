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

3. Start server

    ```bash
    python manage.py runserver
    ```

# ToDo's

* Add returns
* Add authentication
* Pack product into executables
* ...
