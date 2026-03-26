# ----------- django specific ---------------
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# ----------- utils ---------------------------
from ledger.utils import habit_utils, date_utils, friend_utils

# ------------ forms/models --------------------
from ledger.forms import HabitTrackerForm
from ledger.models import HabitTracker, UserProfile, Nudge, Friendship
from ledger.utils import date_utils as _date_utils

def _get_streak_and_points(user_profile):
    ht = HabitTracker.objects.filter(
        user=user_profile,
        month=_date_utils.get_first_of_this_month()
    ).first()
    if ht:
        return ht.streak, ht.points
    return 0, 0
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
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
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

            # log empty habits until today (exclusive)
            habit_utils.create_empty_days_until_today(date_utils.get_first_of_this_month(), habit_tracker)

            return redirect('ledger:myhabits')
    else:
        if not habit_utils.check_if_any_habits_added(habit_tracker): 
            form = HabitTrackerForm()

            context_dict['form'] = form
            return render(request, 'ledger/create_habit_tracker.html', context=context_dict)
        else:
            from ledger.models import Day, BoolHabitEntry
            today = date_utils.today()
            day, _ = Day.objects.get_or_create(
                habit_tracker=habit_tracker, date=today,
                defaults={'completed_on_day': False}
            )
            for habit in habit_tracker.habits.all():
                BoolHabitEntry.objects.get_or_create(day=day, habit=habit, defaults={'done': False})

            context_dict['entries'] = day.bool_habit_entries.select_related('habit').all()
            context_dict['streak'] = habit_tracker.streak
            context_dict['points'] = habit_tracker.points
            return render(request, 'ledger/myhabits.html', context=context_dict)





def leaderboards(request):
    context_dict = {}

    return render(request, 'ledger/leaderboards.html', context=context_dict)



@login_required
def social(request):
    from ledger.models import FriendRequest
    tab = request.GET.get('tab', 'search').strip()
    query = request.GET.get('q', '').strip()
    current_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_list = []

    if tab == 'friends':
        friendships = Friendship.objects.filter(user=current_profile).select_related('friend__user')
        if query:
            friendships = friendships.filter(friend__user__username__icontains=query)
        for friendship in friendships:
            friend_profile = friendship.friend
            streak, points = _get_streak_and_points(friend_profile)
            user_list.append({
                'id': friend_profile.id,
                'username': friend_profile.user.username,
                'streak': streak,
                'points': points,
                'show_add_button': False,
            })

    elif tab == 'requests':
        pending = FriendRequest.objects.filter(
            requested=current_profile,
            status=FriendRequest.PENDING
        ).select_related('requester__user')
        for req in pending:
            user_list.append({
                'id': req.requester.id,
                'request_id': req.id,
                'username': req.requester.user.username,
            })

    else:
        tab = 'search'
        friend_ids = Friendship.objects.filter(user=current_profile).values_list('friend_id', flat=True)
        pending_sent_ids = FriendRequest.objects.filter(
            requester=current_profile,
            status=FriendRequest.PENDING
        ).values_list('requested_id', flat=True)
        users = User.objects.exclude(id=request.user.id)
        if query:
            users = users.filter(username__icontains=query)
        for user in users:
            try:
                profile = user.userprofile
            except UserProfile.DoesNotExist:
                continue
            streak, points = _get_streak_and_points(profile)
            already_friend = profile.id in friend_ids
            request_pending = profile.id in pending_sent_ids
            user_list.append({
                'id': profile.id,
                'username': user.username,
                'streak': streak,
                'points': points,
                'show_add_button': not already_friend and not request_pending,
                'request_pending': request_pending,
                'already_friend': already_friend,
            })

    return render(request, 'social/social.html', {
        'user_list': user_list,
        'query': query,
        'active_tab': tab,
    })


@login_required
def send_friend_request(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    from ledger.models import FriendRequest
    data = json.loads(request.body)
    receiver_profile_id = data.get('user_id')
    current_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    try:
        receiver = UserProfile.objects.get(id=receiver_profile_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)
    already_friends = Friendship.objects.filter(user=current_profile, friend=receiver).exists()
    already_requested = FriendRequest.objects.filter(
        requester=current_profile, requested=receiver, status=FriendRequest.PENDING
    ).exists()
    if already_friends or already_requested:
        return JsonResponse({'error': 'already friends or pending'}, status=400)
    friend_utils.make_friend_request(current_profile, receiver)
    return JsonResponse({'status': 'ok'})


@login_required
def handle_friend_request(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    from ledger.models import FriendRequest
    data = json.loads(request.body)
    request_id = data.get('request_id')
    action = data.get('action')
    try:
        freq = FriendRequest.objects.get(id=request_id, requested=UserProfile.objects.get_or_create(user=request.user)[0])
    except FriendRequest.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)
    if action == 'accept':
        friend_utils.accept_friend_request(freq.requester, freq.requested)
    elif action == 'reject':
        friend_utils.reject_friend_request(freq.requester, freq.requested)
    else:
        return JsonResponse({'error': 'invalid action'}, status=400)
    return JsonResponse({'status': 'ok'})

def profile(request, username=None):
    if username is None:
        if request.user.is_authenticated:
            username = request.user.username
        else:
            from django.shortcuts import redirect
            return redirect('/login/')

    try:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return render(request, 'ledger/404.html', status=404)

    picture_url = user_profile.picture.url if user_profile.picture else '/media/guest.jpg'

    friend_count = friend_utils.get_friends_for_user(user_profile).count()

    context_dict = {
        'profile_user': user,
        'profile': user_profile,
        'picture_url': picture_url,
        'friend_count': friend_count,
        'is_own_profile': request.user == user,
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


@login_required
def log_habit_entry(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    from ledger.models import BoolHabitEntry, Day, Habit
    from ledger.utils.habit_utils import calculate_points_for_one

    data = json.loads(request.body)
    entry_id = data.get('entry_id')
    done = bool(data.get('done', False))

    try:
        entry = BoolHabitEntry.objects.select_related(
            'day__habit_tracker__user__user', 'habit'
        ).get(id=entry_id)
    except BoolHabitEntry.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    if entry.day.habit_tracker.user != UserProfile.objects.get_or_create(user=request.user)[0]:
        return JsonResponse({'error': 'forbidden'}, status=403)

    entry.done = done
    entry.save()

    day = entry.day
    habit_tracker = day.habit_tracker

    # recalculate completed_on_day: all DO done, all DONT not done, all EASY_WIN done
    all_entries = day.bool_habit_entries.select_related('habit').all()
    completed = all(
        (e.done if e.habit.habit_type in (Habit.TYPE_DO, Habit.TYPE_EASY_WIN) else not e.done)
        for e in all_entries
        if e.habit.habit_type != Habit.TYPE_NUMERIC
    )
    day.completed_on_day = completed
    day.save()

    habit_tracker.refresh_streak()

    total_points = sum(calculate_points_for_one(d) for d in habit_tracker.days.all())
    habit_tracker.points = total_points
    habit_tracker.save(update_fields=['points'])

    return JsonResponse({'streak': habit_tracker.streak, 'points': habit_tracker.points})


def get_notifications(request):
    # only nudges for now
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=403)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

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

@login_required
def mark_notifications_read(request):
    # only nudges for now
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    # update nudges
    Nudge.objects.filter(nudged=user_profile, notified=False).update(notified=True)
    # return okay response
    return JsonResponse({"status": "ok"})
