# Generated by Django 5.2.1 on 2025-06-04 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tasklog',
            options={'ordering': ['start_time']},
        ),
    ]
