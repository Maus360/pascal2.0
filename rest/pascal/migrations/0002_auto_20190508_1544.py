# Generated by Django 2.2.1 on 2019-05-08 15:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pascal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='post_date',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]
