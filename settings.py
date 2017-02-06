# -*- coding: utf-8 -*-
import datetime

with open('api_token.txt', 'r') as fh:
    api_token = fh.readline().rstrip()

# Date format used in settings, messages and input parameters.
# Note it might be different from Toggl.date_format
date_format = "%Y-%m-%d"

# start_date is a date of first report. I.e. to get first report for Jan 5-11,
# first date should be Jan 12 end_date is a date of last report. I.e. if
# semester ends 2015-05-08, it is next monday (May 11)
start_date = '2016-01-02'
end_date = '2016-05-23'

# generate reports for last month by default
# [today-timeframe .. today] to be specific
# timeframe = datetime.timedelta(days=30)
timeframe = datetime.timedelta(days=30)

workspace2meta = {
    'YORSO': 'YORSO',
    'YORSO2': 'YORSO',
    u"Минимакс": u"Минимакс"
}

# Format string for date date representation in report,
# https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
report_date_format = "%b %d"
