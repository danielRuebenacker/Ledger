from django.test import TestCase

# ---------- models -----------
from ledger.models import *
from django.urls import reverse
from .test_factories import UserProfileFactory

# utils
from ledger.utils import date_utils

class TestNudges(TestCase):

    def setUp(self):
        self.userDjango1 = UserProfileFactory(user__username="gave")
        self.userDjango2 = UserProfileFactory(user__username="receives")
    
    def test_get_notifications_fail(self):
        result = self.client.get(reverse('ledger:notifications'))

        self.assertEqual(result.status_code, 403)

    def test_get_notifications(self):
        nudge = Nudge.objects.get_or_create(nudger=self.userDjango1, nudged=self.userDjango2)

        self.client.force_login(self.userDjango2.user)

        result = self.client.get(reverse('ledger:notifications'))

        self.assertEquals(result.status_code, 200) 

        data = result.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["nudger"], self.userDjango1.user.username)

    def test_mark_notifications_read(self):     
         self.client.force_login(self.userDjango2.user)
         result = self.client.get(reverse('ledger:mark_notifications_read'))
         
         self.assertEquals(result.json()["status"], "ok") 
       
class TestLeaderboard(TestCase):
    def setUp(self):
        self.userDjango1 = UserProfileFactory(user__username="first")
        self.user1HabitTracker = HabitTracker.objects.get_or_create(user=self.userDjango1, streak = 5, points=10)

        self.userDjango2 = UserProfileFactory(user__username="second")
        self.user2HabitTracker = HabitTracker.objects.get_or_create(user=self.userDjango2, streak = 3, points=5)

        self.userDjango3 = UserProfileFactory(user__username="third")
        self.user3HabitTracker = HabitTracker.objects.get_or_create(user=self.userDjango3, streak = 1, points=2)
    
    def test_leaderboard_under(self):
        self.client.force_login(self.userDjango1.user)

        result = self.client.get(reverse('ledger:leaderboards'))

        self.assertEqual(result.status_code, 200)

        self.assertEqual(result.context['top_points'][0].user.user.username, self.userDjango1.user.username)

        self.assertEqual(result.context['top_points'][1].user.user.username, self.userDjango2.user.username)

        self.assertEqual(result.context['top_points'][2].user.user.username, self.userDjango3.user.username)

class TestProfile(TestCase):
    def setUp(self):
        self.userDjango1 = UserProfileFactory(user__username="user1")
        self.userDjango2 = UserProfileFactory(user__username="user2")
    
    def test_redirect_not_found(self):
        self.client.force_login(self.userDjango1.user)

        result = self.client.get(reverse('ledger:profile_user', kwargs={'username': 'does_not_exist'}))

        self.assertEqual(result.status_code, 404)
