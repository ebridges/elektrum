# Generated by Django 3.0.8 on 2020-09-07 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_items', '0008_auto_20190512_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediaitem',
            name='focal_length',
            field=models.CharField(
                help_text='Optional. The focal length setting used with this media item was created.',
                max_length=16,
                null=True,
                verbose_name='focal length',
            ),
        ),
    ]
