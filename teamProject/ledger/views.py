from django.http import HttpResponse
from django.shortcuts import render
from .models import UserProfile, Friendship, Nudge
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile, Friendship, FriendRequest
from django.contrib.auth.models import User

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

    return render(request, 'ledger/profile.html', context=context_dict)

