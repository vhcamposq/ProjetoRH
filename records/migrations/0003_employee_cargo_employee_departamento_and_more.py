# Generated by Django 4.2.1 on 2023-05-30 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_remove_employee_chamado'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='cargo',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='employee',
            name='departamento',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='employee',
            name='empresa',
            field=models.CharField(default='', max_length=50),
        ),
    ]
