# ------------------ django stuff
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# -------------- models
from ledger.models import UserProfile
from django.contrib.auth.models import User

# ------------------ utils --------------
from ledger.utils.habit_utils import get_all_months_data, create_habit, get_log_data, save_log
from ledger.utils.friends import get_friends_for_user

# ------------ other ------
from datetime import date, datetime
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

    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}

    return render(request, 'ledger/leaderboards.html', context=context_dict)

def social(request):
    context_dict = {}

    return render(request, 'ledger/social.html', context=context_dict)

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

    friend_count = get_friends_for_user(user_profile).count()

    context_dict = {
        'profile_user': user,
        'profile': user_profile,
        'picture_url': picture_url,
        'friend_count': friend_count,
        'is_own_profile': request.user == user,
    }
    return render(request, 'ledger/profile.html', context=context_dict)

@login_required
def myhabits_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    months = get_all_months_data(user_profile)
    return JsonResponse({'months': months})

@login_required
@require_POST
def create_habit_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    name = request.POST.get('name', '').strip()
    habit_type = request.POST.get('habit_type', '')
    points = request.POST.get('points', '0')

    habit, error = create_habit(name, habit_type, points, user_profile)
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

        groups, journal_text, log_date = get_log_data(user_profile, log_date)
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

    error = save_log(user_profile, log_date, checked_ids, journal_text)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': True})

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
