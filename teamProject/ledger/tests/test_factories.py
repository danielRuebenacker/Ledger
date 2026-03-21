# factory_boy 
import factory

# ledger specific models 
from django.contrib.auth.models import User
from ledger.models import BoolHabitEntry, Habit, HabitTracker, Day
from ledger.models import UserProfile

# our helper date utilities (e.g. provides get_first_of_this_month)
from ledger.utils import date

# factory for base user model (not used directly)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = "test"


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile
    # use subfactory for dependent models
    user = factory.SubFactory(UserFactory)

class HabitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Habit
    is_community = True
    habit_type = Habit.TYPE_DO
    points = 10

class HabitTrackerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HabitTracker
    user = factory.SubFactory(UserProfileFactory)
    # lazy = only call when necessary
    month = factory.LazyFunction(date.get_first_of_this_month)
    # add habits once initialised...

class DayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day
    habit_tracker = factory.SubFactory(HabitTrackerFactory)
    date = factory.LazyFunction(date.today)
    completed_on_day = True

class BoolHabitEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BoolHabitEntry
    day = factory.SubFactory(DayFactory)
    habit = factory.SubFactory(HabitFactory)
    done = True
    
