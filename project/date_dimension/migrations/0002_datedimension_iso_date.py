# Generated by Django 2.1.7 on 2019-05-12 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('date_dimension', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datedimension',
            name='iso_date',
            field=models.CharField(default='2001-09-11', help_text='Required. YYYY-MM-DD as a string.', max_length=16, verbose_name='This date formatted as an ISO date (i.e. yyyy-mm-dd)'),
            preserve_default=False,
        ),
    ]
