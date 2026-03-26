from django.contrib import admin
from ledger.models import (
    UserProfile, Habit, Nudge, Friendship, HabitTracker, 
    Day, BoolHabitEntry, JournalEntry, FriendRequest
)

@admin.register(HabitTracker)
class HabitTrackerAdmin(admin.ModelAdmin):
    # This defines the columns that appear in the admin table
    list_display = ('user', 'month', 'streak')
    
    # This adds a sidebar to filter data by month or streak value
    list_filter = ('month', 'streak')

# Register the remaining models normally
admin.site.register(BoolHabitEntry)
admin.site.register(Day)
admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(Habit)
admin.site.register(JournalEntry)
admin.site.register(Nudge)
admin.site.register(UserProfile)