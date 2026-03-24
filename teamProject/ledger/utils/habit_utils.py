from ledger.models import UserProfile, HabitTracker, Day, Habit, BoolHabitEntry
from ledger.utils import date_utils

def get_user_habit_trackers(user):
    return list(user.habit_trackers.all().order_by('month'))

def get_current_month_habit_tracker(user):
    # here user is a user profile
    this_month = date_utils.get_first_of_this_month()
    # get this months habit tracker
    habit_tracker = HabitTracker.objects.get_or_create(user=user)

def get_habit_tracker_habit_entries(habit_tracker):
    # this method takes a habit tracker and fetches all habit entries and organises them into a dict
    # by days. i.e. days is a dict of day keys to habit entry list values
    days = habit_tracker.days
    # stores collection of habit entries
    day_habits = {}
    for day in days:
        boolean_habit_entries = day.bool_habit_entries
        day_habits[day] = boolean_habit_entries
    return day_habits


def get_day(habit_tracker, date):
    # date is a datetime object
    return Day.objects.get_or_create(habit_tracker=habit_tracker, date=date)

def get_or_create_habits_from_list(habit_strings, habit_type):
    habits = []
    for habit_string in habit_strings:
        # by default: not community + zero points 
        # exactly what we want if habit not already created
        habit, created = Habit.objects.get_or_create(name=habit_string, habit_type=habit_type)
        habits.append(habit)
    return habits

def register_habits_with_habit_tracker(habits, habit_tracker):
    habit_tracker.habits.add(*habits)

def get_or_create_habits_then_register(dos_strings, donts_strings, easy_wins_strings, numeric_strings, habit_tracker):
    dos = get_or_create_habits_from_list(dos_strings, Habit.TYPE_DO)
    donts = get_or_create_habits_from_list(donts_strings, Habit.TYPE_DONT)
    easy_wins = get_or_create_habits_from_list(easy_wins_strings, Habit.TYPE_EASY_WIN)
    numeric = get_or_create_habits_from_list(numeric_strings, Habit.TYPE_NUMERIC)
    habits = [dos, donts, easy_wins, numeric]
    
    for habit_type in habits:
         register_habits_with_habit_tracker(habit_type, habit_tracker)


def log_bool_habit(habit_tracker, habit, done, date):
    # bool habit entry needs: day, habit, and done
    # date tracker is a datetime object
    # if we are logging it's got to be this month
    day = get_day(habit_tracker=habit_tracker, date=date)
    bool_habit_entry = BoolHabitEntry.objects.create(day=day, habit=habit, done=done)
    return bool_habit_entry

def calculate_streak(user):
    habit_tracker = get_current_month_habit_tracker(user)
    if habit_tracker is None: return
    # reverse ordering by date
    days = habit_tracker.days.order_by("-date")
    streak = 0
    for day in days:
        if not day.completed_on_the_day:
            return streak
        streak += 1

def create_empty_habit_entries_for_day(habit_tracker, date, habits):
    for habit in habits:
        # all false
        log_bool_habit(habit_tracker=habit_tracker, habit=habit, done=False, date=date)


def create_empty_days_until_today(date, habit_tracker):
    # day: datetime object
    habits = habit_tracker.habits
    for single_date in date_utils.daterange(date, date.today()):
        create_empty_habit_entries_for_day(habit_tracker, single_date, habits)
