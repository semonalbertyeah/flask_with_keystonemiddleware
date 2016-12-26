# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta
from datetime import datetime
from calendar import timegm

def is_whole_hour(utc_time):
    """
        input:
            utc_time -> (utc) timestamp or datetime.
    """
    if isinstance(utc_time, datetime):
        if (utc_time.microsecond == 0) and \
           (utc_time.second == 0) and \
           (utc_time.minute == 0):
            return True
        else:
            return False
    else:
        return float(utc_time) % 3600 == 0


def is_whole_day(utc_time):
    """
        input:
            utc_time -> (utc) timestamp or datetime.
    """
    if not isinstance(utc_time, datetime):
        utc_time = datetime.utcfromtimestamp(float(utc_time))

    if not is_whole_hour(utc_time):
        return False

    return utc_time.hour == 0


def is_whole_week(utc_time):
    """
        input:
            utc_time -> (utc) timestamp or datetime.
    """
    if not isinstance(utc_time, datetime):
        utc_time = datetime.utcfromtimestamp(float(utc_time))

    if not is_whole_day(utc_time):
        return False

    return utc_time.weekday() == 0    # monday



def is_whole_month(utc_time):
    """
        input:
            utc_time -> (utc) timestamp or datetime.
    """
    if not isinstance(utc_time, datetime):
        utc_time = datetime.utcfromtimestamp(float(utc_time))

    if not is_whole_day(utc_time):
        return False

    return utc_time.day == 1


def is_whole_year(utc_time):
    """
        input:
            utc_time -> (utc) timestamp or datetime.
    """
    if not isinstance(utc_time, datetime):
        utc_time = datetime.utcfromtimestamp(float(utc_time))

    if not is_whole_month(utc_time):
        return False

    return utc_time.month == 1


def datetime_2_utctimestamp(dt):
    """
        datetime to utc timestamp
    """
    return timegm(dt.utctimetuple())


def timestamp_natural_sub(timestamp, **fields):
    """
        timetamp subtraction (natural calendar)
    """
    delta = {}
    if fields.has_key('years'):
        delta['years'] = fields['years']
    if fields.has_key('months'):
        delta['months'] = fields['months']
    if fields.has_key('days'):
        delta['days'] = fields['days']
    if fields.has_key('hours'):
        delta['hours'] = fields['hours']
    if fields.has_key('minutes'):
        delta['minutes'] = fields['minutes']
    if fields.has_key('seconds'):
        delta['seconds'] = fields['seconds']
    if fields.has_key('microseconds'):
        delta['microseconds'] = fields['microseconds']

    dt = datetime.utcfromtimestamp(timestamp)
    return datetime_2_utctimestamp(dt - relativedelta(**delta))
 


def timestamp_natural_add(timestamp, **fields):
    """
        timestamp addition (natural calendar)
    """
    delta = {}
    if fields.has_key('years'):
        delta['years'] = fields['years']
    if fields.has_key('months'):
        delta['months'] = fields['months']
    if fields.has_key('days'):
        delta['days'] = fields['days']
    if fields.has_key('hours'):
        delta['hours'] = fields['hours']
    if fields.has_key('minutes'):
        delta['minutes'] = fields['minutes']
    if fields.has_key('seconds'):
        delta['seconds'] = fields['seconds']
    if fields.has_key('microseconds'):
        delta['microseconds'] = fields['microseconds']

    dt = datetime.utcfromtimestamp(timestamp)
    return datetime_2_utctimestamp(dt + relativedelta(**delta))


