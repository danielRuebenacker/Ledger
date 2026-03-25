# ----------- django specific ---------------
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# ----------- utils ---------------------------
from ledger.utils import habit_utils, date, friends

# ------------ models --------------------
from ledger.models import HabitTracker, UserProfile, Nudge
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


def get_notifications(request):
    # only nudges for now
    user = request.user
    user_profile = user.userprofile
    if not user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=403)

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
