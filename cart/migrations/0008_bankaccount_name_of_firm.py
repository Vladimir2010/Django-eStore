# Generated by Django 3.2.20 on 2023-07-27 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0007_auto_20230727_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccount',
            name='name_of_firm',
            field=models.BooleanField(default=False),
        ),
    ]
