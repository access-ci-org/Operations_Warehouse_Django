# Generated by Django 4.1.12 on 2024-03-15 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_state', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publisherinfo',
            name='Location',
            field=models.CharField(max_length=200, null=True),
        ),
    ]