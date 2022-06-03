# Generated by Django 4.0 on 2022-02-14 23:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0004_alter_user_creation_date_alter_user_last_use'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 14, 23, 19, 13, 875784, tzinfo=utc), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_use',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 14, 23, 19, 13, 875825, tzinfo=utc), verbose_name='Дата последнего использования'),
        ),
    ]
