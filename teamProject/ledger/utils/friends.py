from ledger.models import UserProfile, Friendship, FriendRequest
from datetime import datetime


def get_friends_for_user(user):
    friendships = Friendship.objects.filter(user=user)
    return friendships

def make_friend_request(sender, receiver):
    friend_request = FriendRequest.objects.create(requester=sender, requested=receiver))

def get_friend_request(sender, receiver):
    try:
        friend_request = FriendRequest.objects.get(requester=sender, requested=receiver)
    except FriendRequest.DoesNotExist:
        # friend request does not exist in database
        print(f"Friend request from {sender} to {receiver} does not exist in the db.")
    else:
        return friend_request
     

def accept_friend_request(sender, receiver):
    # update friendrequest metadata
    friend_request = get_friend_request(sender, receiver)
    if not friend_request:
        return
    friend_request.status = FriendRequest.ACCEPTED
    friend_request.date_accepted = datetime.today
    friend_request.save()
    # make friendship entries in friendship table
    _ = Friendship.objects.create(user=sender, friend=receiver)
    # create reverse relationship too
    _ = Friendship.objects.create(user=receiver, friend=sender)

def reject_friend_request(user, rejected_user):
    friend_request = get_friend_request(sender, receiver)
    if not friend_request:
        return
    friend_request.status = FriendRequest.REJECTED
    friend_request.save()


def get_user_friend_requests(user):
    friend_requests = FriendRequest.objects.filter(requested=user)
    return friend_requests


