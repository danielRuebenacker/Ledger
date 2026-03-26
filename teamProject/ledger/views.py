# ----------- django specific ---------------
from datetime import date, datetime
from django.views.decorators.http import require_POST

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# ----------- utils ---------------------------
from ledger.utils import habit_utils, date_utils, friend_utils

# ------------ forms/models --------------------
from ledger.forms import HabitTrackerForm
from ledger.models import HabitTracker, UserProfile, Nudge, Friendship
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

@login_required
def myhabits(request):
    context_dict = {}
    user_profile = request.user.userprofile
    # if habit tracker is not created present form view
    habit_tracker, _ = HabitTracker.objects.get_or_create(user=user_profile, month=date_utils.get_first_of_this_month())

    
    if request.method == 'POST':
        form = HabitTrackerForm(request.POST)

        if form.is_valid():
            # ignore empty strings
            clean = lambda x: x.strip().lower()

            # get all cleaned data, and clean according to our clean
            habit_string_lists = [
                    [clean(h) for h in form.cleaned_data.get(f, []) if h] 
                    for f in ('dos', 'donts', 'easy_wins', 'numeric')
            ]

            # makes into habits/gets habit then adds to habit tracker
            habit_utils.get_or_create_habits_then_register(*habit_string_lists, habit_tracker)
    else:
        if not habit_utils.check_if_any_habits_added(habit_tracker): 
            form = HabitTrackerForm()

            context_dict['form'] = form
            # the create habit tracker partial will be displayed
            context_dict['display_create_tracker'] = True
            
    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}

    return render(request, 'ledger/myhabits.html', context=context_dict)

def social(request):
    context_dict = {}

    return render(request, 'ledger/social.html', context=context_dict)

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
        already_nudged = Nudge.objects.filter(
            nudger=logged_in_profile,
            nudged=user_profile,
            date_of_nudge__date=today
        ).exists()

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
def myhabits_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    months = habit_utils.get_all_months_data(user_profile)
    return JsonResponse({'months': months})

@login_required
@require_POST
def create_habit_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    name = request.POST.get('name', '').strip()
    habit_type = request.POST.get('habit_type', '')

    habit, error = habit_utils.create_habit(name, habit_type, user_profile)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': True, 'name': habit.name})

@login_required
def log_habits_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    today = date.today()

    if request.method == 'GET':
        log_date_str = request.GET.get('date', today.isoformat())
        try:
            log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        except ValueError:
            log_date = today

        groups, journal_text, log_date = habit_utils.get_log_data(user_profile, log_date)
        return JsonResponse({
            'groups': groups,
            'journal': journal_text,
            'date': log_date.isoformat(),
        })

    # POST — save the log
    log_date_str = request.POST.get('date', today.isoformat())
    try:
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date.'}, status=400)

    checked_ids = request.POST.getlist('habits')
    journal_text = request.POST.get('journal', '').strip()

    error = habit_utils.save_log(user_profile, log_date, checked_ids, journal_text)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': True})



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
