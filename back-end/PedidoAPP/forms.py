# forms.py
from django import forms

class UploadOrderForm(forms.Form):
    file = forms.FileField()


