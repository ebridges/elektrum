# Generated by Django 2.1.4 on 2019-01-18 11:03

import collection.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='id')),
                ('path', models.CharField(error_messages={'unique': 'A collection with that path already exists.'}, help_text='Required. Path to media collection from the root of your archive.', max_length=1024, unique=True, validators=[collection.models.CollectionPathValidator()], verbose_name='collection path')),
                ('user', models.ForeignKey(help_text='User that owns this collection', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'collection',
            },
        ),
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together={('path', 'user')},
        ),
    ]
