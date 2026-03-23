from django.http import HttpResponse
from django.shortcuts import render
from .models import UserProfile, Friendship, Nudge
from django.contrib.auth.decorators import login_required

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
    if not request.user.is_authenticated:
        return redirect('/login/')

    current_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    friendships = Friendship.objects.filter(user=current_profile).select_related('friend__user')
    friends_list = []
    for friendship in friendships:
        friend_profile = friendship.friend
        friends_list.append({
            'id': friend_profile.id,
            'username': friend_profile.user.username,
            'streak': 0,
            'points': 0,
        })

    query = request.GET.get('q', '').strip()
    search_results = []
    if query:
        profiles = UserProfile.objects.exclude(id=current_profile.id).filter(
            user__username__icontains=query
        ).select_related('user')

        for profile in profiles:
            is_friend = Friendship.objects.filter(
                user=current_profile,
                friend=profile
            ).exists()

            friend_request = (
                FriendRequest.objects.filter(
                    requester=current_profile,
                    requested=profile
                ).first()
                or
                FriendRequest.objects.filter(
                    requester=profile,
                    requested=current_profile
                ).first()
            )

            if is_friend:
                button_state = 'friends'
            elif friend_request and friend_request.status == FriendRequest.PENDING:
                button_state = 'pending'
            else:
                button_state = 'add'

            search_results.append({
                'id': profile.id,
                'username': profile.user.username,
                'button_state': button_state,
            })

    return render(request, 'social/social.html', {
        'friends_list': friends_list,
        'search_results': search_results,
        'query': query,
    })

def profile(request):
    context_dict = {}

    return render(request, 'ledger/profile.html', context=context_dict)

