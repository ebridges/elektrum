# Generated by Django 2.1.7 on 2019-05-10 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('date_dimension', '0001_initial'), ('media_items', '0006_auto_20190506_1714')]

    operations = [
        migrations.AddField(
            model_name='mediaitem',
            name='create_day',
            field=models.ForeignKey(
                help_text='The date the media item was created.',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='date_dimension.DateDimension',
            ),
        )
    ]
