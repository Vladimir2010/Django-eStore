# Generated by Django 3.2.20 on 2023-07-27 06:54

import cart.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_rename_банковисметки_банкови_сметки'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('first_name_bg', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('last_name_bg', models.CharField(max_length=100, null=True)),
                ('iban', models.CharField(max_length=22, unique=True, validators=[cart.validators.check_bank_account])),
                ('iban_bg', models.CharField(max_length=22, null=True, unique=True, validators=[cart.validators.check_bank_account])),
                ('bic', models.CharField(max_length=100)),
                ('bic_bg', models.CharField(max_length=100, null=True)),
                ('bank_name', models.CharField(max_length=100)),
                ('bank_name_bg', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Банкови_Сметки',
        ),
    ]
