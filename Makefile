SHELL := /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.load-venv:
	source $(ROOT_DIR)/venv/bin/activate

run: .load-venv
	python manage.py runserver

migrate: .load-venv
	python manage.py migrate

make-migrations: .load-venv
	python manage.py makemigrations invoice

make-messages: .load-venv
	( \
		cd $(ROOT_DIR); \
		python manage.py makemessages -l=ru -l=en -i=venv/*; \
	)

compile-messages: .load-venv
	( \
		cd $(ROOT_DIR)/invoice; \
		python ../manage.py compilemessages -l=en -l=ru --settings=invoices.settings; \
		cd ../; \
	)
