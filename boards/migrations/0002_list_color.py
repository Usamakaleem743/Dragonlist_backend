# Generated by Django 5.1.7 on 2025-03-23 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='color',
            field=models.CharField(default='#0079bf', max_length=50),
        ),
    ]
