# Generated by Django 5.0.14 on 2025-05-13 17:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration_badges', '0002_alter_resource_badge_task_workflow_status_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource_badge',
            name='badge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badge_resource_set', to='integration_badges.badge'),
        ),
    ]
