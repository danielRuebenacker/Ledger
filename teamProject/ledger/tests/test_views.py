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
       

