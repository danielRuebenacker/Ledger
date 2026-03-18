from django.test import TestCase
from ledger.utils import habit_utils, date
from .test_factories import *
from datetime import datetime

class TestHabitTrackerGet(TestCase):
    def test_get_habit_tracker(self):
        habit_tracker = HabitTrackerFactory()
        user = habit_tracker.user
        util_habit_tracker = habit_utils.get_current_month_habit_tracker(user=user)
        self.assertEquals(habit_tracker, util_habit_tracker)

    # def test_get_all_user_habit_trackers(self):
    #     user = UserProfileFactory()
    #     # feb = date.get_first_day_of_month(datetime.)
    #     _ = HabitTrackerFactory(user=user)
    #     _ = HabitTrackerFactory(user=user)
    #     _ = HabitTrackerFactory(user=user)
    #     _ = HabitTrackerFactory(user=user)
    #     habit_trackers = habit_utils.get_user_habit_trackers(user=user)
    #     self.assertEquals(habit_trackers, user.habit_trackers.all())
