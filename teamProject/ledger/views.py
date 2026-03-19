from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import UserProfile, Friendship, Nudge
from django.utils import timezone

# Create your views here.

def index(request):
    context_dict = {}
    return render(request, 'social/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}
    return render(request, 'social/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}
    return render(request, 'social/leaderboards.html', context=context_dict)

def social(request):
    current_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    sent = Friendship.objects.filter(requester=current_profile, status=Friendship.ACCEPTED)
    received = Friendship.objects.filter(requested=current_profile, status=Friendship.ACCEPTED)

    friends_list = []
    for f in sent:
        p = f.requested
        friends_list.append({'username': p.user.username, 'streak': 0, 'points': 0})
    for f in received:
        p = f.requester
        friends_list.append({'username': p.user.username, 'streak': 0, 'points': 0})

    query = request.GET.get('q', '').strip()
    search_results = []
    if query:
        profiles = UserProfile.objects.exclude(id=current_profile.id).filter(
            user__username__icontains=query
        )
        for profile in profiles:
            friendship = Friendship.objects.filter(
                requester=current_profile, requested=profile
            ).first() or Friendship.objects.filter(
                requester=profile, requested=current_profile
            ).first()

            if friendship:
                if friendship.status == Friendship.PENDING:
                    button_state = 'pending'
                elif friendship.status == Friendship.ACCEPTED:
                    button_state = 'friends'
                else:
                    button_state = 'add'
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
    return render(request, 'social/friends.html', context=context_dict)



@login_required
def requests_page(request):
    current_profile, created = UserProfile.objects.get_or_create(user=request.user)

    action = request.GET.get('action', '').strip()
    friendship_id = request.GET.get('id', '').strip()

    message = ''
    show_friends_link = False

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
                show_friends_link = True
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
        'show_friends_link': show_friends_link,
    }
    return render(request, 'social/requests.html', context_dict)

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
                if existing_friendship.status == Friendship.PENDING:
                    error_message = f'Friend request already sent to {target_profile.user.username}.'
                elif existing_friendship.status == Friendship.ACCEPTED:
                    error_message = f'You are already friends with {target_profile.user.username}.'
                elif existing_friendship.status == Friendship.REJECTED:
                    existing_friendship.requester = current_profile
                    existing_friendship.requested = target_profile
                    existing_friendship.status = Friendship.PENDING
                    existing_friendship.date_accepted = None
                    existing_friendship.save()
                    added_user = target_profile.user.username
            else:
                Friendship.objects.create(
                    requester=current_profile,
                    requested=target_profile,
                    status=Friendship.PENDING
                )
                added_user = target_profile.user.username

    search_results = []

    if query:
        profiles = UserProfile.objects.exclude(id=current_profile.id).filter(
            user__username__icontains=query
        )

        search_results = []
        for profile in profiles:
            friendship = Friendship.objects.filter(
                requester=current_profile,
                requested=profile
            ).first() or Friendship.objects.filter(
                requester=profile,
                requested=current_profile
            ).first()

            if friendship:
                if friendship.status == Friendship.PENDING:
                    button_state = 'pending'
                elif friendship.status == Friendship.ACCEPTED:
                    button_state = 'friends'
                else:
                    button_state = 'add'
            else:
                button_state = 'add'

            search_results.append({
                'id': profile.id,
                'username': profile.user.username,
                'button_state': button_state,
            })

    context_dict = {
        'search_results': search_results,
        'query': query,
        'added_user': added_user,
        'error_message': error_message,
    }
    return render(request, 'social/search.html', context=context_dict)


@login_required
def nudge_page(request):
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
            'id': friend_profile.id,
            'username': friend_profile.user.username,
        })

    for friendship in received_accepted:
        friend_profile = friendship.requester
        friends_list.append({
            'id': friend_profile.id,
            'username': friend_profile.user.username,
        })

    preselected_friend = request.GET.get('friend', '').strip()

    success_message = ''
    error_message = ''
    message_text = ''
    selected_friend = preselected_friend

    if request.method == 'POST':
        selected_friend = request.POST.get('sent_to', '').strip()
        message_text = request.POST.get('message', '').strip()

        valid_friend_names = [friend['username'] for friend in friends_list]

        if not friends_list:
            error_message = 'You need at least one friend before sending a nudge.'
        elif not selected_friend:
            error_message = 'Please select a friend before sending a nudge.'
        elif selected_friend not in valid_friend_names:
            error_message = 'You can only send nudges to your friends.'
        elif not message_text:
            error_message = 'Please write a message before sending a nudge.'
        else:
            target_profile = UserProfile.objects.filter(user__username=selected_friend).first()

            if target_profile:
                Nudge.objects.create(
                    nudger=current_profile,
                    nudged=target_profile,
                    message=message_text
                )
                success_message = f'Nudge sent to {selected_friend}.'
                message_text = ''

    context_dict = {
        'friends_list': friends_list,
        'sent_to': selected_friend,
        'message_text': message_text,
        'success_message': success_message,
        'error_message': error_message,
    }
    return render(request, 'social/nudge.html', context_dict)

@login_required
def nudge_inbox(request):
    current_profile, created = UserProfile.objects.get_or_create(user=request.user)

    success_message = ''

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'reply':
            nudge_id = request.POST.get('nudge_id', '').strip()
            reply_message = request.POST.get('reply_message', '').strip()

            nudge = Nudge.objects.filter(id=nudge_id, nudged=current_profile).first()

            if nudge and reply_message:
                nudge.reply_message = reply_message
                nudge.date_of_reply = timezone.now()
                nudge.save()
                success_message = f'Reply sent to {nudge.nudger.user.username}.'

        elif action == 'delete_one':
            nudge_id = request.POST.get('nudge_id', '').strip()
            nudge = Nudge.objects.filter(id=nudge_id, nudged=current_profile).first()

            if nudge:
                nudge.delete()
                success_message = 'Nudge deleted.'

        elif action == 'delete_all':
            Nudge.objects.filter(nudged=current_profile).delete()
            success_message = 'All received nudges deleted.'

    received_nudges = Nudge.objects.filter(
        nudged=current_profile
    ).order_by('date_of_reply', '-date_of_nudge')

    context_dict = {
        'received_nudges': received_nudges,
        'success_message': success_message,
    }
    return render(request, 'social/nudge_inbox.html', context_dict)

@login_required
def nudge_sent(request):
    current_profile, created = UserProfile.objects.get_or_create(user=request.user)

    success_message = ''

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'delete_one':
            nudge_id = request.POST.get('nudge_id', '').strip()
            nudge = Nudge.objects.filter(id=nudge_id, nudger=current_profile).first()

            if nudge:
                nudge.delete()
                success_message = 'Sent nudge deleted.'

        elif action == 'delete_all':
            Nudge.objects.filter(nudger=current_profile).delete()
            success_message = 'All sent nudges deleted.'

    sent_nudges = Nudge.objects.filter(
        nudger=current_profile
    ).order_by('-date_of_nudge')

    context_dict = {
        'sent_nudges': sent_nudges,
        'success_message': success_message,
    }
    return render(request, 'social/nudge_sent.html', context_dict)