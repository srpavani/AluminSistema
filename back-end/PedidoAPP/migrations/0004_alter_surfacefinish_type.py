# Generated by Django 5.1.1 on 2024-09-13 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PedidoAPP', '0003_company_typecompany'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surfacefinish',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
