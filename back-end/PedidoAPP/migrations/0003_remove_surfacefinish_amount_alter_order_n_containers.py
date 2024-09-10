# Generated by Django 5.1.1 on 2024-09-10 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PedidoAPP', '0002_alter_order_n_containers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surfacefinish',
            name='amount',
        ),
        migrations.AlterField(
            model_name='order',
            name='n_containers',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]
