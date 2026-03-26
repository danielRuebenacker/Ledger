import calendar

from ledger.utils import date_utils
from datetime import date, timedelta

from ledger.models import BoolHabitEntry, Day, Habit, HabitTracker, JournalEntry

def check_if_any_habits_added(habit_tracker):
    return habit_tracker.habits.exists()

def get_user_habit_trackers(user):
    return list(user.habit_trackers.all().order_by('month'))

def get_current_month_habit_tracker(user):
    from ledger.models import HabitTracker
    # get this months habit tracker
    habit_tracker, _ = HabitTracker.objects.get_or_create(user=user)
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

def calculate_streak(user):
    habit_tracker = get_current_month_habit_tracker(user)
    if habit_tracker is None: return
    days = habit_tracker.days.order_by("-date")
    streak = 0
    for day in days:
        if not day.completed_on_the_day:
            return streak
        streak += 1


# Data builders used by API views

TYPE_ORDER = [
    ('do', 'Must DOs', '\u2705'),
    ('dont', "Must DON'Ts", '\u274c'),
    ('easy_win', 'Small Wins', '\U0001F3C6'),
]

HABIT_GROUPS_TEMPLATE = {
    'do': {'label': 'Must DOs', 'emoji': '\u2705', 'habits': []},
    'dont': {'label': "Must DON'Ts", 'emoji': '\u274c', 'habits': []},
    'easy_win': {'label': 'Small Wins', 'emoji': '\U0001F3C6', 'habits': []},
}

def build_month_data(tracker):
    month_label = tracker.month.strftime('%B %Y')
    num_days = calendar.monthrange(tracker.month.year, tracker.month.month)[1]

    # Journal entries indexed by day number
    journals = {}
    days_map = {}
    for day in tracker.days.all():
        days_map[day.date.day] = day
        j = JournalEntry.objects.filter(day=day).first()
        if j:
            journals[day.date.day] = j.journal_text

    journal_list = []
    for d in range(1, num_days + 1):
        journal_list.append({
            'day': d,
            'text': journals.get(d, ''),
        })

    # Habit grid grouped by type
    sections = []
    for type_key, label, emoji in TYPE_ORDER:
        habits_of_type = [h for h in tracker.habits.all() if h.habit_type == type_key]
        if not habits_of_type:
            continue
        habit_columns = []
        for habit in habits_of_type:
            grid = []
            for d in range(1, num_days + 1):
                done = False
                if d in days_map:
                    entry = BoolHabitEntry.objects.filter(day=days_map[d], habit=habit).first()
                    if entry and entry.done:
                        done = True
                grid.append(done)
            habit_columns.append({
                'name': habit.name,
                'grid': grid,
            })
        sections.append({
            'label': label,
            'emoji': emoji,
            'habits': habit_columns,
        })

    return {
        'month': month_label,
        'num_days': num_days,
        'journals': journal_list,
        'sections': sections,
    }


def get_all_months_data(user_profile):
    trackers = HabitTracker.objects.filter(user=user_profile).order_by('month')
    return [build_month_data(t) for t in trackers]


def create_habit(name, habit_type, user_profile):
    if not name:
        return None, 'Name is required.'

    valid_types = [c[0] for c in Habit.HABIT_TYPE_CHOICES]
    if habit_type not in valid_types:
        return None, 'Invalid habit type.'

    if Habit.objects.filter(name=name).exists():
        return None, 'A habit with that name already exists.'

    habit = Habit.objects.create(name=name, habit_type=habit_type)

    today = date.today()
    first_of_month = today.replace(day=1)
    tracker, _ = HabitTracker.objects.get_or_create(user=user_profile, month=first_of_month)
    tracker.habits.add(habit)

    return habit, None


def get_log_data(user_profile, log_date):
    import copy
    groups = copy.deepcopy(HABIT_GROUPS_TEMPLATE)

    today = date.today()
    first_of_month = today.replace(day=1)
    tracker = HabitTracker.objects.filter(user=user_profile, month=first_of_month).first()

    if not tracker:
        return list(groups.values()), '', log_date

    day_obj = Day.objects.filter(habit_tracker=tracker, date=log_date).first()
    journal_text = ''
    if day_obj:
        j = JournalEntry.objects.filter(day=day_obj).first()
        if j:
            journal_text = j.journal_text

    for habit in tracker.habits.all():
        checked = False
        if day_obj:
            entry = BoolHabitEntry.objects.filter(day=day_obj, habit=habit).first()
            if entry:
                checked = entry.done
        groups[habit.habit_type]['habits'].append({
            'id': habit.id,
            'name': habit.name,
            'checked': checked,
        })

    return [g for g in groups.values() if g['habits']], journal_text, log_date


def save_log(user_profile, log_date, checked_ids, journal_text):
    today = date.today()
    first_of_month = today.replace(day=1)
    tracker = HabitTracker.objects.filter(user=user_profile, month=first_of_month).first()

    if not tracker:
        tracker = HabitTracker.objects.create(user=user_profile, month=first_of_month)

    day_obj, _ = Day.objects.get_or_create(habit_tracker=tracker, date=log_date)

    for habit in tracker.habits.all():
        entry, _ = BoolHabitEntry.objects.get_or_create(day=day_obj, habit=habit)
        entry.done = str(habit.id) in checked_ids
        entry.save()

    j = JournalEntry.objects.filter(day=day_obj).first()
    if journal_text:
        if j:
            j.journal_text = journal_text
            j.save()
        else:
            JournalEntry.objects.create(day=day_obj, journal_text=journal_text)
    elif j:
        j.delete()
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
