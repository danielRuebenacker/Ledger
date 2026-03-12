from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import Friendship, UserProfile
from django.utils import timezone

# Create your views here.

def index(request):
    context_dict = {}
    return render(request, 'ledger/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}
    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}
    return render(request, 'ledger/leaderboards.html', context=context_dict)

def social(request):
    context_dict = {}
    return render(request, 'ledger/social.html', context=context_dict)


@login_required
def friends(request):
    current_profile, created = UserProfile.objects.get_or_create(user=request.user)

    sent_accepted = Friendship.objects.filter(
        requester=current_profile,
        status=Friendship.ACCEPTED
    )

    received_accepted = Friendship.objects.filter(
        requested=current_profile,
        status=Friendship.ACCEPTED
    )

    friends_list = []

    for friendship in sent_accepted:
        friend_profile = friendship.requested
        friends_list.append({
            'username': friend_profile.user.username,
        })

    for friendship in received_accepted:
        friend_profile = friendship.requester
        friends_list.append({
            'username': friend_profile.user.username,
        })

    context_dict = {
        'friends_list': friends_list,
    }
    return render(request, 'ledger/friends.html', context=context_dict)



@login_required
def requests_page(request):
    current_profile, created = UserProfile.objects.get_or_create(user=request.user)

    action = request.GET.get('action', '').strip()
    friendship_id = request.GET.get('id', '').strip()

    message = ''

    if action and friendship_id:
        friendship = Friendship.objects.filter(
            id=friendship_id,
            requested=current_profile,
            status=Friendship.PENDING
        ).first()

        if friendship:
            if action == 'accept':
                friendship.status = Friendship.ACCEPTED
                friendship.date_accepted = timezone.now().date()
                friendship.save()
                message = f'Friend request from {friendship.requester} accepted.'
            elif action == 'reject':
                friendship.status = Friendship.REJECTED
                friendship.save()
                message = f'Friend request from {friendship.requester} rejected.'

    incoming_requests = Friendship.objects.filter(
        requested=current_profile,
        status=Friendship.PENDING
    )

    sent_requests = Friendship.objects.filter(
        requester=current_profile,
        status=Friendship.PENDING
    )

    context_dict = {
        'incoming_requests': incoming_requests,
        'sent_requests': sent_requests,
        'message': message,
    }
    return render(request, 'ledger/requests.html', context_dict)



@login_required
def search_users(request):
    current_profile, created = UserProfile.objects.get_or_create(user=request.user)

    query = request.GET.get('q', '').strip()
    add_id = request.GET.get('add_id', '').strip()

    added_user = ''
    error_message = ''

    if add_id:
        target_profile = UserProfile.objects.filter(id=add_id).exclude(id=current_profile.id).first()

        if target_profile:
            existing_friendship = Friendship.objects.filter(
                requester=current_profile,
                requested=target_profile
            ).first() or Friendship.objects.filter(
                requester=target_profile,
                requested=current_profile
            ).first()

            if existing_friendship:
                error_message = f'You already have a friendship record with {target_profile.user.username}.'
            else:
                Friendship.objects.create(
                    requester=current_profile,
                    requested=target_profile,
                    status=Friendship.PENDING
                )
                added_user = target_profile.user.username

    search_results = []

    if query:
        search_results = UserProfile.objects.exclude(
            id=current_profile.id
        ).filter(
            user__username__icontains=query
        )

    context_dict = {
        'search_results': search_results,
        'query': query,
        'added_user': added_user,
        'error_message': error_message,
    }
    return render(request, 'ledger/search.html', context_dict)


def nudge_page(request):
    friends_list = [
        {'name': 'Alice'},
        {'name': 'Ben'},
        {'name': 'Chloe'},
    ]

    sent_to = request.GET.get('sent_to', '').strip()
    message_text = request.GET.get('message', '').strip()

    success_message = ''
    error_message = ''

    if 'sent_to' in request.GET or 'message' in request.GET:
        if not sent_to:
            error_message = 'Please select a friend before sending a nudge.'
        else:
            success_message = f'Nudge sent to {sent_to}.'
            message_text = ''

    context_dict = {
        'friends_list': friends_list,
        'sent_to': sent_to,
        'message_text': message_text,
        'success_message': success_message,
        'error_message': error_message,
    }
    return render(request, 'ledger/nudge.html', context=context_dict)