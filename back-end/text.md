Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser --> liberar uso da venv

python -m venv venv

.\venv\Scripts\activate --> ativar venv

deactivate --> desativar venv

pip install django
pip install djangorestframework
pip install requests

django-admin startproject [nome_do_projeto] .
python manage.py startapp [nome_do_app]

python manage.py makemigrations
python manage.py migrate

python manage.py runserver
python manage.py createsuperuser