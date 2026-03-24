from django.contrib import admin
from ledger.models import UserProfile, Habit, Nudge, Friendship, HabitTracker, Day, BoolHabitEntry, JournalEntry, FriendRequest

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Habit)
admin.site.register(Nudge)
admin.site.register(Friendship)
admin.site.register(HabitTracker)
admin.site.register(Day)
admin.site.register(BoolHabitEntry)
admin.site.register(JournalEntry)
admin.site.register(FriendRequest)