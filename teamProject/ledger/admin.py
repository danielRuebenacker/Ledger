from django.contrib import admin
from ledger.models import UserProfile, Habit, HabitTracker

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Habit)
admin.site.register(HabitTracker)
