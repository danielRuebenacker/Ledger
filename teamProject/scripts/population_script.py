import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(script_dir)

# Add the project root to sys.path so it can find 'teamProject'
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teamProject.settings')

import django
django.setup()

from ledger.models import UserProfile, Habit, Nudge, Friendship, HabitTracker, Day, BoolHabitEntry, JournalEntry, FriendRequest
from django.contrib.auth.models import User
import random
from datetime import datetime
from datetime import timedelta
from ledger.utils.date_utils import get_first_of_this_month

from django.contrib.auth.hashers import make_password

def populate_users():
    first_names = ["Luke", "John", "Bob", "Robert", "Alan", "Gordon", "Michael", "Sam", "Euan", "Mark", "Jeremy"]
    last_names = ["Jones", "Smith", "Miller", "Davis", "Brown", "Stewart"]

    
    users_to_create = []
    
    # 1. Prepare User objects in memory
    for fname in first_names:
        for lname in last_names:
            username = f"{fname}_{lname}"
            users_to_create.append(User(
                username=username,
                password=make_password("insecure")
            ))
    
    # 2. Bulk Create Users
    User.objects.bulk_create(users_to_create)
    
    # 3. Bulk Create Profiles for any User that doesn't have one
    # This handles both newly created users and any orphans
    existing_user_ids_with_profile = UserProfile.objects.values_list('user_id', flat=True)
    users_needing_profile = User.objects.exclude(id__in=existing_user_ids_with_profile)
    
    profiles_to_create = [UserProfile(user=u) for u in users_needing_profile]
    UserProfile.objects.bulk_create(profiles_to_create)

    print(f"Created {len(users_to_create)} users and {len(profiles_to_create)} profiles.")


def populate_habits():
    # Define point constants
    p1, p2, p3 = 1, 2, 3

    # Define all habits
    habits_data = [
        # dos 
        {"name": "Read", "is_community": True, "habit_type": Habit.TYPE_DO, "points": p2},
        {"name": "Walk", "is_community": True, "habit_type": Habit.TYPE_DO, "points": p2},
        {"name": "Study", "is_community": True, "habit_type": Habit.TYPE_DO, "points": p2},
        {"name": "Gym", "is_community": True, "habit_type": Habit.TYPE_DO, "points": p2},
        {"name": "Journal", "is_community": True, "habit_type": Habit.TYPE_DO, "points": p2},

        # donts
        {"name": "Phone before bed", "is_community": True, "habit_type": Habit.TYPE_DONT, "points": p2},
        {"name": "Doomscroll", "is_community": True, "habit_type": Habit.TYPE_DONT, "points": p3},
        {"name": "Caffeine", "is_community": True, "habit_type": Habit.TYPE_DONT, "points": p3},

        # easy Ws
        {"name": "Go outside", "is_community": True, "habit_type": Habit.TYPE_EASY_WIN, "points": p1},
        {"name": "Listen to music", "is_community": True, "habit_type": Habit.TYPE_EASY_WIN, "points": p1},
        {"name": "Coffee", "is_community": True, "habit_type": Habit.TYPE_EASY_WIN, "points": p1},
        {"name": "Phone someone", "is_community": True, "habit_type": Habit.TYPE_EASY_WIN, "points": p1},

        # numeric
        {"name": "Screentime", "is_community": True, "habit_type": Habit.TYPE_EASY_WIN, "points": p3},
        {"name": "Hours of Sleep", "is_community": True, "habit_type": Habit.TYPE_EASY_WIN, "points": p1},
    ]

    # Create habits directly in the database
    for data in habits_data:
        Habit.objects.create(**data)

def populate_friendship():
    users = list(UserProfile.objects.all())
    num_users = len(users)
    
    # Deterministic seed
    random.seed(42)
    p = 25 
    
    requests_to_create = []
    friendships_to_create = []

    for i in range(num_users):
        for j in range(i + 1, num_users):
            if random.randint(0, 100) < p:
                u1, u2 = users[i], users[j]
                
                # Metadata for the request
                days_ago = random.randint(0, 21)
                date = datetime.today() - timedelta(days=days_ago)

                # 1. Prepare the FriendRequest (The record)
                requests_to_create.append(
                    FriendRequest(
                        requester=u1,
                        requested=u2,
                        status="ACCEPTED",
                        date_accepted=date
                    )
                )

                # 2. Prepare the Friendships (The bidirectional link)
                # We create both directions so the relationship is mutual
                friendships_to_create.append(Friendship(user=u1, friend=u2))
                friendships_to_create.append(Friendship(user=u2, friend=u1))

    # Single database hit for requests
    FriendRequest.objects.bulk_create(requests_to_create, ignore_conflicts=True)
    
    # Single database hit for friendships
    Friendship.objects.bulk_create(friendships_to_create, ignore_conflicts=True)

    print(f"Created {len(requests_to_create)} requests and {len(friendships_to_create)} friendship links.")

def populate_trackers():
    random.seed(42)  # Deterministic results
    users = list(UserProfile.objects.all())
    all_habits = list(Habit.objects.all())
    first_of_month = get_first_of_this_month()
    
    # Containers for bulk creation
    trackers_to_create = []
    days_to_create = []
    habit_entries = []
    journal_entries = []
    m2m_relations = []

    # 1. Create Trackers with dummy leaderboard data
    for user in users:
        # Generate random dummy data for leaderboards
        random_streak = random.randint(0, 30) #
        random_points = random.randint(0, 500) #
        
        trackers_to_create.append(
            HabitTracker(
                user=user, 
                month=first_of_month,
                streak=random_streak, # Assign random streak
                points=random_points  # Assign random points
            )
        )
    
    # Bulk create trackers first so they get IDs
    HabitTracker.objects.bulk_create(trackers_to_create, ignore_conflicts=True)
    
    # Re-fetch trackers to associate them with days/habits
    trackers = HabitTracker.objects.filter(month=first_of_month)

    # 2. Build Days and Entries in memory
    for tracker in trackers:
        # Assign a random but deterministic subset of habits to this tracker
        p_threshold = random.randint(20, 50)
        selected_habits = [h for h in all_habits if random.randint(0, 100) < p_threshold]
        
        # Prepare ManyToMany links (HabitTracker <-> Habit)
        for h in selected_habits:
            m2m_relations.append(HabitTracker.habits.through(habittracker_id=tracker.id, habit_id=h.id))

        # Create 3-7 days for each tracker
        num_days = random.randint(3, 7)
        for i in range(num_days):
            date = datetime.today().date() - timedelta(days=i)
            day_obj = Day(habit_tracker=tracker, date=date, completed_on_day=True)
            days_to_create.append(day_obj)

    # Bulk create Days
    Day.objects.bulk_create(days_to_create, ignore_conflicts=True)
    
    # 3. Create Habit and Journal Entries
    # Fetch days back with their tracker/habit info to link entries
    all_days = Day.objects.filter(habit_tracker__month=first_of_month).select_related('habit_tracker')
    
    # Map tracker IDs to their selected habits to avoid re-calculating
    tracker_habit_map = {}
    for rel in m2m_relations:
        tracker_habit_map.setdefault(rel.habittracker_id, []).append(rel.habit_id)

    for day in all_days:
        # Add Journal Entry
        journal_entries.append(JournalEntry(day=day, journal_text=f"Journal for {day.date}"))
        
        # Add BoolHabitEntries for each habit in the tracker
        habit_ids = tracker_habit_map.get(day.habit_tracker_id, [])
        for h_id in habit_ids:
            habit_entries.append(BoolHabitEntry(day=day, habit_id=h_id, done=True))

    # Final Bulk Operations
    HabitTracker.habits.through.objects.bulk_create(m2m_relations, ignore_conflicts=True)
    JournalEntry.objects.bulk_create(journal_entries)
    BoolHabitEntry.objects.bulk_create(habit_entries)

    print(f"Populated {len(trackers_to_create)} trackers with random leaderboard data, days, and entries.")

def create_admin():
    username = "admin"
    password = "admin"

    admin, _ = User.objects.get_or_create(username=username)
    admin.set_password(password)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    profile, _ = UserProfile.objects.get_or_create(user=admin)
    # trust 
    profile.theme = UserProfile.DARK
    profile.save()

    print(f"Created admin user: {username} and password: {password} (insecure). Only for testing purposes.")

def run():
    populate_users()
    print("POPULATE USERS")

    populate_habits()
    print("POPULATE HABITS")

    populate_friendship()
    print("POPULATE FRIENDS")

    populate_trackers()
    print("POPULATE TRACKERS")

    create_admin()
    print("CREATE ADMIN")

        
if __name__ == '__main__':
    run()
