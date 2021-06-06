import pytz

from dateutil.relativedelta import relativedelta
from datetime import datetime


class Dater(object):
    def now():
        return datetime.now(pytz.timezone('Europe/Stockholm'))

    def today():
        now = Dater.now()
        return datetime(now.year, now.month, now.day)

    def in_3_months():
        return Dater.today() + relativedelta(months=3)
