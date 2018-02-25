import datetime


HOUR_SECONDS = 3600
DAY_SECONDS  = 86400
WEEK_SECONDS = 604800


def get_datetime_elements(dt):
    iso_datetime = dt.isoformat()
    iso_calendar = dt.isocalendar()
    print(iso_datetime)
    print(iso_calendar)
    return {
        'year': iso_datetime[0:4],
        'month': iso_datetime[5:7],
        'day': iso_datetime[8:10],
        'hour': iso_datetime[11:13],
        'year_week': "{:04d}-{:02d}".format(iso_calendar[0], iso_calendar[1])
    }


dt1 = datetime.datetime(2017, 1, 1,  0,  0,  0)
dt2 = datetime.datetime(2017, 1, 1, 12,  0,  0)
dt3 = datetime.datetime(2017, 1, 1, 17, 59, 59)
dt4 = datetime.datetime(2018, 1, 1, 23, 59, 59)
print(get_datetime_elements(dt1))
print(get_datetime_elements(dt2))
print(get_datetime_elements(dt3))
print(get_datetime_elements(dt4))



