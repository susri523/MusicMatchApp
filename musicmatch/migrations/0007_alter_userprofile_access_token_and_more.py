# Generated by Django 4.0 on 2021-12-28 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicmatch', '0006_merge_20211228_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='access_token',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='refresh_token',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]