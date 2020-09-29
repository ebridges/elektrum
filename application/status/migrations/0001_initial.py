# Generated by Django 3.0.8 on 2020-09-15 02:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import media_items.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessorLog',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name='id',
                    ),
                ),
                ('event_date', models.DateTimeField(verbose_name='Event date.')),
                (
                    'file_path',
                    models.CharField(
                        help_text='Required. Path to media item from the root of users archive.',
                        max_length=4096,
                        validators=[media_items.models.MediaItemPathValidator()],
                        verbose_name='file path',
                    ),
                ),
                (
                    'error_code',
                    models.CharField(
                        help_text='Required. Classification of the error.',
                        max_length=64,
                        verbose_name='Error code',
                    ),
                ),
                (
                    'message',
                    models.CharField(
                        help_text='Required. Error message.',
                        max_length=4096,
                        verbose_name='Error message',
                    ),
                ),
                (
                    'reason',
                    models.CharField(
                        help_text='Optional. Reason for the error, e.g. stacktrace.',
                        max_length=8192,
                        null=True,
                        verbose_name='Error message',
                    ),
                ),
                (
                    'original_file_path',
                    models.CharField(
                        help_text='Optional. Path to media item that was uploaded.',
                        max_length=4096,
                        null=True,
                        verbose_name='original file path',
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        help_text='Required. User that owns this media item',
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={'abstract': False,},
        ),
    ]
