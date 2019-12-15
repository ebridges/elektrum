from django.db import migrations, models
from datetime import date
from date_dimension.scripts.generate_date_dimensions import date_range


def create_date_dimension_rows():
    start_date = date(1970, 1, 1)
    end_date = date(2050, 12, 31)
    for d in date_range(start_date, end_date):
        yield migrations.RunSQL(
            [
                (
                    'INSERT INTO date_dim(yyyymmdd,this_date,year,month,day,week_num,week_day,day_in_year,iso_date) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);',
                    [
                        d['yyyymmdd'],
                        d['this_date'],
                        d['year'],
                        d['month'],
                        d['day'],
                        d['week_num'],
                        d['week_day'],
                        d['day_in_year'],
                        d['iso_date'],
                    ],
                )
            ],
            [('DELETE FROM date_dim where yyyymmdd=%s;', [d['yyyymmdd']])],
        )


class Migration(migrations.Migration):

    dependencies = [('date_dimension', '0002_datedimension_iso_date')]

    operations = create_date_dimension_rows()
