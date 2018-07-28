#!/usr/bin/env python

from dateutil import rrule
import datetime as dt
import itertools as it
from pprint import pprint

def date_list(start, end):
    start = dt.date(start.year, start.month, 1)
    end = dt.date(end.year, end.month, 1)
    dates = [t for t in rrule.rrule(rrule.DAILY, dtstart=start, until=end)]
    return dates

def get_last_days_in_month_list(dates):
    last_days = []
    for k, g in it.groupby(dates, lambda x: x.month):
        last_days.append(list(g)[-1])

    return last_days

def get_all_days_except_last(dates):
    days = []
    for k, g in it.groupby(dates, lambda x: x.month):
        alldays = list(g)
        if len(alldays) > 1:
            days.append(alldays[:-1])
    return days

def get_test_dates():
    return date_list(dt.datetime(2018, 1, 1), dt.datetime(2018, 7, 1))

if __name__ == "__main__":
    pprint(get_last_days_in_month_list(get_test_dates()))
    pprint(get_all_days_except_last(get_test_dates()))
