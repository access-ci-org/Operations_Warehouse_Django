# Generated by Django 4.1.13 on 2024-07-23 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration_badges', '0003_integration_resource_badge_badge_access_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration_workflow',
            name='comment',
            field=models.TextField(null=True),
        ),
    ]