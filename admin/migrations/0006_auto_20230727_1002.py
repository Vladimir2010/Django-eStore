# Generated by Django 3.2.20 on 2023-07-27 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_auto_20230727_0954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bankaccount',
            name='bank_name_bg',
        ),
        migrations.RemoveField(
            model_name='bankaccount',
            name='bic_bg',
        ),
        migrations.RemoveField(
            model_name='bankaccount',
            name='first_name_bg',
        ),
        migrations.RemoveField(
            model_name='bankaccount',
            name='iban_bg',
        ),
        migrations.RemoveField(
            model_name='bankaccount',
            name='last_name_bg',
        ),
    ]