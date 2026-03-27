# ----------- django specific ---------------
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.shortcuts import redirect, render, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

# ----------- utils ---------------------------
from ledger.utils import habit_utils, date_utils, friend_utils

# ------------ forms/models --------------------
from ledger.forms import HabitTrackerForm, CustomRegistrationForm, LogHabitForm, CreateHabitForm
from ledger.models import HabitTracker, UserProfile, Nudge, Friendship, FriendRequest, Day, JournalEntry, BoolHabitEntry, Habit
from django.db.models import Q
from django.contrib.auth.models import User

# ------------ json/files -----------
from django.http import JsonResponse
import json
import os

# Create your views here.

def index(request):
    context_dict = {}

    return render(request, 'ledger/index.html', context=context_dict)

def log_habits_view(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile
        form = LogHabitForm(request.POST, user_profile=user_profile)

        if form.is_valid():
            # extract cleaned data
            log_date = form.cleaned_data['date']
            journal_text = form.cleaned_data['journal_text']
            selected_habits = form.cleaned_data['habits']
            habit_tracker = habit_utils.get_current_month_habit_tracker(user_profile)

            existing_day = Day.objects.filter(habit_tracker=habit_tracker, date=log_date).first()
            if existing_day and existing_day.completed_on_day:
                messages.add_message(request, messages.ERROR, "Cannot log habit for day already logged")
                return redirect(reverse('ledger:myhabits'))

            day_obj = habit_utils.get_day(habit_tracker=habit_tracker, date=log_date)
            if log_date == date_utils.today():
                day_obj.completed_on_day = True
                day_obj.save()

            if journal_text:
                JournalEntry.objects.update_or_create( day=day_obj, defaults={'journal_text': journal_text})

            # First, get all habits associated with this tracker
            all_tracker_habits = habit_tracker.habits.all()

            points = 0
            for habit in all_tracker_habits:
                # If the habit was checked in the form, done=True, otherwise False
                is_done = habit in selected_habits
                
                BoolHabitEntry.objects.update_or_create( day=day_obj, habit=habit, defaults={'done': is_done})
                if is_done:
                    points += habit.points
            
            # update points & streaks
            habit_tracker.refresh_streak()
            habit_tracker.points = points
            
    return redirect(reverse('ledger:myhabits'))

def create_habit_view(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile
        form = CreateHabitForm(request.POST)

        if form.is_valid():
            # can't just form.save() as need get_or_create
            name = form.cleaned_data['name'].strip().title()
            habit_type = form.cleaned_data['habit_type']

            habit, _ = Habit.objects.get_or_create(name=name, habit_type=habit_type)

            tracker = habit_utils.get_current_month_habit_tracker(user_profile)
            tracker.habits.add(habit)
            tracker.save()

    return redirect(reverse('ledger:myhabits'))

def create_habit_tracker_view(request):
    user_profile = request.user.userprofile
    habit_tracker = habit_utils.get_current_month_habit_tracker(user=user_profile)

    if request.method == 'POST':
        form = HabitTrackerForm(request.POST)

        if form.is_valid():
            # ignore empty strings
            clean = lambda x: x.strip().title()

            # get all cleaned data, and clean according to our clean
            habit_string_lists = [
                    [clean(h) for h in form.cleaned_data.get(f, []) if h] 
                    for f in ('dos', 'donts', 'easy_wins')
            ]

            # makes into habits/gets habit then adds to habit tracker
            habit_utils.get_or_create_habits_then_register(*habit_string_lists, habit_tracker)
    return redirect(reverse('ledger:myhabits'))

@login_required
def myhabits(request):
    context_dict = {}
    user_profile = request.user.userprofile
    habit_tracker = habit_utils.get_current_month_habit_tracker(user=user_profile)

    months_data = habit_utils.get_all_months_data(user_profile)
    context_dict = {
            'months': months_data,
            'log_form': LogHabitForm(user_profile=user_profile),
            'create_form': CreateHabitForm(),
    }
    context_dict['show_empty_state'] = len(months_data) == 0

    if not habit_utils.check_if_any_habits_added(habit_tracker): 
        form = HabitTrackerForm()

        context_dict['form'] = form
        # the create habit tracker partial will be displayed
        context_dict['display_create_tracker'] = True
            
    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    from ledger.utils import date_utils
    from ledger.models import HabitTracker
 
    this_month = date_utils.get_first_of_this_month()
 
    top_streaks = (HabitTracker.objects.filter(month=this_month, streak__gt=0).select_related('user__user').order_by('-streak')[:50])
 
    top_points = (HabitTracker.objects.filter(month=this_month, points__gt=0).select_related('user__user').order_by('-points')[:50])
 
    current_streak_rank = None
    current_points_rank = None
 
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            tracker = HabitTracker.objects.get(user=user_profile, month=this_month)
 
            streak_rank = HabitTracker.objects.filter(month=this_month, streak__gt=tracker.streak).count() + 1
 
            points_rank = HabitTracker.objects.filter(month=this_month, points__gt=tracker.points).count() + 1
 
            current_streak_rank = streak_rank if streak_rank <= 50 else None
            current_points_rank = points_rank if points_rank <= 50 else None
 
        except HabitTracker.DoesNotExist:
            pass
 
    context_dict = {
        'top_streaks': top_streaks,
        'top_points': top_points,
        'current_streak_rank': current_streak_rank,
        'current_points_rank': current_points_rank,
    }
 
    return render(request, 'ledger/leaderboards.html', context=context_dict)

def social(request):
    query = request.GET.get('q', '').strip()
    active_tab = request.GET.get('tab', 'search')
    user_profile = request.user.userprofile

    users_with_status = []
    friends = []
    friend_requests = []

    if active_tab == 'search':
        if query:
            users_qs = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
        else:
            users_qs = User.objects.exclude(id=request.user.id).order_by('username')[:10]

        sent_requests = FriendRequest.objects.filter(requester=user_profile).values_list('requested_id', flat=True)
        current_friends = Friendship.objects.filter(user=user_profile).values_list('friend_id', flat=True)

        for u in users_qs:
            try:
                target_p = u.userprofile
                status = 'none'
                if target_p.id in current_friends:
                    status = 'friend'
                elif target_p.id in sent_requests:
                    status = 'pending'
                users_with_status.append({'user': u, 'status': status})
            except UserProfile.DoesNotExist:
                continue

    elif active_tab == 'friends':
        friendships = Friendship.objects.filter(user=user_profile)
        friends = [f.friend for f in friendships]
        if query:
            friends = [f for f in friends if query.lower() in f.user.username.lower()]

    elif active_tab == 'requests':
        friend_requests = FriendRequest.objects.filter(requested=user_profile)

    context_dict = {
        'active_tab': active_tab,
        'query': query,
        'users_with_status': users_with_status,
        'friends': friends,
        'friend_requests': friend_requests,
    }
    return render(request, 'ledger/social.html', context=context_dict)

@require_POST
def add_friend_request(request):
    data = json.loads(request.body)
    target_user_id = data.get('user_id')
    
    try:
        receiver = User.objects.get(id=target_user_id).userprofile
        sender = request.user.userprofile
        
        FriendRequest.objects.get_or_create(requester=sender, requested=receiver)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
def handle_friend_request(request):
    data = json.loads(request.body)
    request_id = data.get('request_id')
    action = data.get('action')
    
    try:
        f_req = FriendRequest.objects.get(id=request_id, requested=request.user.userprofile)
        if action == 'accept':
            Friendship.objects.get_or_create(user=f_req.requester, friend=f_req.requested)
            Friendship.objects.get_or_create(user=f_req.requested, friend=f_req.requester)
            f_req.delete()
            return JsonResponse({'status': 'accepted'})
        elif action == 'reject':
            f_req.delete()
            return JsonResponse({'status': 'rejected'})
    except FriendRequest.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

def profile(request, username=None):
    if username is None:
        if request.user.is_authenticated:
            username = request.user.username
        else:
            return redirect('/login/')

    try:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return render(request, 'ledger/404.html', status=404)

    picture_url = user_profile.picture.url if user_profile.picture else '/media/guest.jpg'
    friend_count = friend_utils.get_friends_for_user(user_profile).count()

    try:
        tracker = HabitTracker.objects.get(user=user_profile, month=date_utils.get_first_of_this_month())
        streak = tracker.streak
    except HabitTracker.DoesNotExist:
        tracker = None
        streak = 0

    is_friend = False
    logged_in_profile = None
    if request.user.is_authenticated and request.user != user:
        try:
            logged_in_profile = UserProfile.objects.get(user=request.user)
            is_friend = Friendship.objects.filter(
                Q(user=logged_in_profile, friend=user_profile) |
                Q(user=user_profile, friend=logged_in_profile)
            ).exists()
        except UserProfile.DoesNotExist:
            pass

    already_nudged = False
    if is_friend and logged_in_profile:
        today = timezone.now().date()
        already_nudged = Nudge.objects.filter(nudger=logged_in_profile,nudged=user_profile,date_of_nudge__date=today).exists()

    context_dict = {
        'profile_user': user,
        'profile': user_profile,
        'picture_url': picture_url,
        'friend_count': friend_count,
        'streak': streak,
        'tracker': tracker,
        'is_own_profile': request.user == user,
        'is_friend': is_friend,
        'already_nudged': already_nudged,
    }
    return render(request, 'ledger/profile.html', context=context_dict)

@login_required
def settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if request.content_type.startswith('application/json'):
            data = json.loads(request.body)
            theme = data.get('theme')
            about_me = data.get('about_me')

            if theme in ('light', 'dark'):
                profile.theme = theme
                profile.save()
                return JsonResponse({'status': 'ok'})

            if about_me is not None:
                profile.about_me = about_me
                profile.save()
                return JsonResponse({'status': 'ok'})

            return JsonResponse({'status': 'invalid'}, status=400)

        if request.content_type.startswith('multipart/form-data'):
            if 'picture' in request.FILES:
                if profile.picture:
                    if os.path.isfile(profile.picture.path):
                        os.remove(profile.picture.path)
                profile.picture = request.FILES['picture']
                profile.save()
                return JsonResponse({'status': 'ok', 'picture_url': profile.picture.url})
            return JsonResponse({'status': 'no file'}, status=400)

    picture_url = profile.picture.url if profile.picture else '/media/guest.jpg'
    return render(request, 'ledger/settings.html', {'picture_url': picture_url,'about_me': profile.about_me,})

def get_notifications(request):
    # only nudges for now
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=403)
    user_profile = user.userprofile

    # say 20 notifs, reverse ordered
    nudges = Nudge.objects.filter(nudged=user_profile).order_by('-date_of_nudge')[:20]
    data = [
        {
            "nudger": n.nudger.user.username, 
            "notified": n.notified,
            "date": n.date_of_nudge.strftime("%Y-%m-%d %H:%M")
        } 
        for n in nudges]
    # json response only allows dicts so need safe = false to allow list
    return JsonResponse(data, safe=False)

def mark_notifications_read(request):
    # only nudges for now
    user_profile = request.user.userprofile
    # update nudges
    Nudge.objects.filter(nudged=user_profile, notified=False).update(notified=True)
    # return okay response
    return JsonResponse({"status": "ok"})

@login_required
def nudge(request, username):
    if request.method == 'POST':
        try:
            nudger_profile = UserProfile.objects.get(user=request.user)
            nudged_user = User.objects.get(username=username)
            nudged_profile = UserProfile.objects.get(user=nudged_user)
        except (UserProfile.DoesNotExist, User.DoesNotExist):
            return JsonResponse({'status': 'error'}, status=404)

        if not Friendship.objects.filter(
            Q(user=nudger_profile, friend=nudged_profile) |
            Q(user=nudged_profile, friend=nudger_profile)
        ).exists():
            return JsonResponse({'status': 'not friends'}, status=403)

        Nudge.objects.create(nudger=nudger_profile, nudged=nudged_profile)
        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'invalid'}, status=400)

def register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Redirect to login or index after successful registration
            return redirect('ledger:index') 
    else:
        form = CustomRegistrationForm()

    return render(request, 'ledger/registration_form.html', {'form': form})
