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

PRODUTO{
ALUMIFONT CODE,
FACTORY CODE,
IMAGE,
LENGTH (MM),
TEMPER ALLOY,
WEIGHT (M/KG),
TEMPER ALLOY,
WEIGHT (M/KG),
#SURFACE_FINISH

}

SURFACE_FINISH{
MILL FINISH,
SILVER ANODIZED (FAYP01),
WHITE POWDER COAT,
BRONZE ANODIZED (FAYP03),
BLACK ANODIZED (FAYP06),
ELECT. CHAMPAGNE (FAYH02),
WOOD FINISH (FA2134-1),
WOOD FINISH (LIGHT),
RUST FINISH
}



lista de dados que eu preciso pegar;

https://www.metal.com/Aluminum/201102250311   ->cny/mt




