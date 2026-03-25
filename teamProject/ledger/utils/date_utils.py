from datetime import datetime, timedelta

def get_first_of_this_month():
    return get_first_day_of_month(today())

def get_first_day_of_month(date):
    # needed because habit tracker object always stores FIRST of month
    return date.replace(day = 1, second = 0, microsecond = 0)

# decoupling from datetime (don't have to constantly import)
def today():
    return datetime.today()

def get_first_of_n_months_ago(n):
    dt = get_first_of_this_month()
    for _ in range(n):
        dt = get_first_day_of_month(dt) - timedelta(days=1)
    return get_first_day_of_month(dt)

# https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
def daterange(start_date, end_date):
    days = int((end_date - start_date).days)
    for n in range(days):
        yield start_date + timedelta(n)
