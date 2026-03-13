from datetime import datetime

def get_first_of_this_month():
    return get_first_day_of_month(today())

def get_first_day_of_month(date):
    # needed because habit tracker object always stores FIRST of month
    return date.replace(day = 1, second = 0, microsecond = 0)

# decoupling from datetime (don't have to constantly import)
def today():
    return datetime.today()
