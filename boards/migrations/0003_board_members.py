# Generated by Django 5.1.7 on 2025-03-25 13:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0002_list_color'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='members',
            field=models.ManyToManyField(related_name='member_of_boards', through='boards.BoardMember', to=settings.AUTH_USER_MODEL),
        ),
    ]
