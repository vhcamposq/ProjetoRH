# Generated by Django 4.2.1 on 2023-05-31 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0005_alter_employee_lider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='cargo',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='departamento',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='empresa',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='lider',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
