from sys import argv, exit
from os.path import basename
from datetime import timedelta, date


def date_range(start, end):
    end = end + timedelta(1)
    for d in range(int((end-start).days)):
        single_date = start + timedelta(d)
        yield {
            'yyyymmdd': int(single_date.strftime('%Y%m%d')),
            'iso_date': single_date.strftime('%Y-%m-%d'),
            'this_date': date(single_date.year, single_date.month, single_date.day),
            'year': single_date.year,
            'month': single_date.month,
            'day': single_date.day,
            'week_num': single_date.isocalendar()[1],
            'week_day': single_date.isoweekday(),
            'day_in_year': single_date.timetuple().tm_yday
        }


def main(arguments):
    if len(arguments) != 3:
        print("Usage: %s [from:yyyy-mm-dd] [to:yyyy-mm-dd]" % basename(arguments[0]))
        return 1

    dates = []
    for arg in arguments[1:]:
        f = [int(x) for x in arg.split('-')]
        dates.append(date(f[0], f[1], f[2]))

    for i in date_range(dates[0], dates[1]):
        print(i)


if __name__ == "__main__":
    exit(main(argv))
