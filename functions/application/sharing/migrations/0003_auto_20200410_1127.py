# Generated by Django 2.2.12 on 2020-04-10 11:27

from django.db import migrations, models
from sharing.models import Share
from django.contrib.auth import get_user_model


def lookup_shared_by(apps, schema_editor):
    AudienceShare = apps.get_model('sharing', 'AudienceShare')

    for audience_share in AudienceShare.objects.all():
        audience = audience_share.shared_to
        share = audience_share.share
        audience.shared_by = share.shared_by
        audience.save()


class Migration(migrations.Migration):

    dependencies = [('sharing', '0002_auto_20200410_1125')]

    operations = [
        ## Existing FK relation is nullable.
        ##   1. This migration populates all existing fields with a value.
        migrations.RunPython(lookup_shared_by),
        ##   2. This alter statement updates the FK relation to be non-nullable.
        migrations.AlterField(
            model_name='audience',
            name='shared_by',
            field=models.ForeignKey(
                null=True, on_delete=models.deletion.CASCADE, to=get_user_model()
            ),
            preserve_default=False,
        ),
    ]