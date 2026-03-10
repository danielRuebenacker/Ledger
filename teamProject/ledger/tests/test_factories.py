import factory
from django.contrib.auth.models import User
from ledger.models import Habit, HabitTracker, DayTracker
from ledger.models import UserProfile
from datetime import datetime

# helper
def get_first_of_month():
    return datetime.today().replace(day=1)

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
    month = factory.LazyFunction(get_first_of_month)
    # add habits once initialised...

class DayTrackerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DayTracker
    tracker = factory.SubFactory(HabitTrackerFactory)
    date = factory.LazyFunction(datetime.today)
    completed_on_day = True

# class BoolHabitEntryFactory(factory.django.DjangoModelFactory):
#     class Meta
