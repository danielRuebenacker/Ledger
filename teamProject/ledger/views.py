from ledger.models import UserProfile
from ledger.utils.friends import get_friends_for_user
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import os

# Create your views here.

def index(request):
    context_dict = {}

    return render(request, 'ledger/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}

    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}

    return render(request, 'ledger/myhabits.html', context=context_dict)



@login_required
def social(request):
    tab = request.GET.get('tab', 'search').strip()
    query = request.GET.get('q', '').strip()

    user_list = []

    if tab == 'friends':
        current_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        friendships = Friendship.objects.filter(user=current_profile).select_related('friend__user')

        if query:
            friendships = friendships.filter(friend__user__username__icontains=query)

        for friendship in friendships:
            friend_profile = friendship.friend
            user_list.append({
                'id': friend_profile.id,
                'username': friend_profile.user.username,
                'streak': 0,
                'points': 0,
                'show_add_button': False,
            })

    elif tab == 'requests':
        user_list = []

    else:
        users = User.objects.exclude(id=request.user.id)

        if query:
            users = users.filter(username__icontains=query)

        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'streak': 0,
                'points': 0,
                'show_add_button': True,
            })

        tab = 'search'

    return render(request, 'social/social.html', {
        'user_list': user_list,
        'query': query,
        'active_tab': tab,
    })

def profile(request):
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
