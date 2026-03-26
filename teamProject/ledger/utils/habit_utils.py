from ledger.utils import date_utils
from datetime import timedelta

def check_if_any_habits_added(habit_tracker):
    return habit_tracker.habits.exists()

def get_user_habit_trackers(user):
    return list(user.habit_trackers.all().order_by('month'))

def get_current_month_habit_tracker(user):
    from ledger.models import HabitTracker
    # get this months habit tracker
    habit_tracker, _ = HabitTracker.objects.get_or_create(user=user, month=date_utils.get_first_of_this_month())
    return habit_tracker

def get_habit_tracker_habit_entries(habit_tracker):
    # this method takes a habit tracker and fetches all habit entries and organises them into a dict
    # by days. i.e. days is a dict of day keys to habit entry list values
    days = habit_tracker.days.all()
    # stores collection of habit entries
    day_habits = {}
    for day in days:
        boolean_habit_entries = day.bool_habit_entries
        day_habits[day] = boolean_habit_entries
    return day_habits


def get_day(habit_tracker, date):
    from ledger.models import Day
    # date is a datetime object
    day, _ = Day.objects.get_or_create(habit_tracker=habit_tracker, date=date, defaults = {'completed_on_day': False})
    return day

def get_or_create_habits_from_list(habit_strings, habit_type):
    from ledger.models import Habit
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
    from ledger.models import Habit
    dos = get_or_create_habits_from_list(dos_strings, Habit.TYPE_DO)
    donts = get_or_create_habits_from_list(donts_strings, Habit.TYPE_DONT)
    easy_wins = get_or_create_habits_from_list(easy_wins_strings, Habit.TYPE_EASY_WIN)
    numeric = get_or_create_habits_from_list(numeric_strings, Habit.TYPE_NUMERIC)
    habits = [dos, donts, easy_wins, numeric]
    
    for habit_type in habits:
         register_habits_with_habit_tracker(habit_type, habit_tracker)

def log_bool_habit(habit, done, day):
    from ledger.models import BoolHabitEntry
    bool_habit_entry, _ = BoolHabitEntry.objects.get_or_create(day=day, habit=habit, defaults={'done': done})
    return bool_habit_entry

def supply_form_with_popular_habits(habit_type):
    from ledger.models import Habit
    return list(
            Habit.objects.filter(
                habit_type=habit_type, 
                is_community=True
            ).order_by('-points')[:10].values_list('name', flat=True)
        )

def calculate_streak(tracker):
    # 1. Get the current day (local time)
    today = date_utils.today()
    
    # 2. Start checking from today (or yesterday if today isn't done yet)
    # If today is finishe start at today. If not start at yesterday
    current_day = today
    today_record = tracker.days.filter(date=today).first()
    
    if not today_record or not today_record.completed_on_day:
        current_day = today - timedelta(days=1)
        
    streak = 0
    
    # 3. Loop backwards one day at a time
    while True:
        day_record = tracker.days.filter(date=current_day, completed_on_day=True).first()
        
        if day_record:
            streak += 1
            current_day -= timedelta(days=1)
        else:
            # Streak broken
            break
            
    return streak



def calculate_points_for_one(day):
    from ledger.models import Habit
    if day.completed_on_day == False:
        return 0

    points = 0

    for entry in day.bool_habit_entries.all():
        habit = entry.habit
        # DOS
        if habit.habit_type == Habit.TYPE_DO and entry.done:
            points += habit.points 
        # DONTS
        if habit.habit_type == Habit.TYPE_DONT and not entry.done:
            points += habit.points 
    return points
