# Generated by Django 3.2.7 on 2022-06-13 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import formio.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Builder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('internal_title', models.CharField(max_length=80)),
                ('internal_description', models.TextField(blank=True)),
                ('form', models.JSONField(default=formio.models.builder_form_default)),
                ('version', models.PositiveIntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('builder_version', models.PositiveIntegerField()),
                ('data', models.JSONField()),
                ('metadata', models.JSONField(default=None, null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('builder', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='formio.builder')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
            ],
        ),
    ]
