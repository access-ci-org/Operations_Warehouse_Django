# Generated by Django 4.1.13 on 2024-07-11 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cider', '0002_alter_ciderinfrastructure_project_affiliation'),
        ('integration_badges', '0002_alter_integration_badge_prerequisite_badge_badge_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration_resource_badge',
            name='badge_access_url',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='integration_resource_badge',
            name='badge_access_url_label',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='integration_resource_badge',
            name='resource_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_badges', to='cider.ciderinfrastructure'),
        ),
        migrations.AlterField(
            model_name='integration_resource_roadmap',
            name='resource_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_roadmaps', to='cider.ciderinfrastructure'),
        ),
        migrations.CreateModel(
            name='Integration_Workflow',
            fields=[
                ('workflow_id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=20)),
                ('stateUpdatedBy', models.CharField(max_length=50)),
                ('stateUpdatedAt', models.DateTimeField(auto_now_add=True)),
                ('badge_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='integration_badges.integration_badge')),
                ('resource_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cider.ciderinfrastructure')),
            ],
        ),
    ]