import json
import random
from datetime import datetime

from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.api.serializers import UserSerializer
from accounts.models import User
from friends.models import Friend, FriendRequest
from helpers.api_error_response import error_response
from notifications.models import Notification

from .serializers import FriendRequestSerializer, FriendSerializer


# Get user friends
# -----------------------------------------------
@api_view(["GET"])
def getFriends(request):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id

    try:
        data = Friend.objects.filter(Q(user_a=user_id) | Q(user_b=user_id))
        friends = [
            entry.user_a if entry.user_a is not user_id else entry.user_b
            for entry in data
        ]
        if friends:
            users = User.objects.filter(id__in=friends)
            users_dict = [UserSerializer(user).data for user in users]
            return Response(data=users_dict, status=status.HTTP_200_OK)
        return Response(
            data=error_response("No friends found!"), status=status.HTTP_404_NOT_FOUND
        )
    except Friend.DoesNotExist:
        return Response(
            data=error_response("No friends found!"), status=status.HTTP_404_NOT_FOUND
        )


# Get user friend requests
# -----------------------------------------------
@api_view(["GET"])
def getFriendRequests(request):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id

    data = FriendRequest.objects.filter(to_user=user_id)
    friendrequests = []
    if data:
        for fr in data:
            # Check if user exist or if accounts id deleted
            try:
                users = User.objects.get(id=fr.from_user)
                userSerializer = UserSerializer(users)
                friendrequests.append(
                    {
                        **userSerializer.data,
                        **{
                            "from_user": fr.from_user,
                            "to_user": fr.to_user,
                            "request_id": fr.id,
                            "since": fr.since,
                        },
                    }
                )
            except User.DoesNotExist:
                FriendRequest.objects.get(pk=fr.id).delete()
        return Response(data=dict(requests=friendrequests), status=status.HTTP_200_OK)
    return Response(
        data=error_response("No friend requests!"), status=status.HTTP_200_OK
    )


# Send friend request to another user
# -----------------------------------------------
@api_view(["POST"])
@csrf_exempt
def sendFriendRequest(request):
    if request.method == "POST":
        # REQUIRED: 'to_user' field in request
        user_id = request.user
        # If user_id type is Response that means we have errored
        if type(user_id) is Response:
            return user_id

        req_dict = request.data

        # Can't send oneself the friend request
        if req_dict["to_user"] == user_id:
            return Response(
                error_response("Cannot send friend request to yourself."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user we are sending request to exist
        if not User.objects.filter(pk=req_dict["to_user"]).exists():
            return Response(
                error_response("User does not exist."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if a friend request from a same use to same user has already been made
        try:
            FriendRequest.objects.get(
                Q(from_user=user_id) & Q(to_user=req_dict["to_user"])
            )
            return Response(
                error_response("Friend request is already sent."),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except FriendRequest.DoesNotExist:
            # Check if these people are already friends
            try:
                Friend.objects.get(
                    Q(user_a=user_id) & Q(user_b=req_dict["to_user"])
                    | Q(user_a=req_dict["to_user"]) & Q(user_b=user_id)
                )
                return Response(
                    error_response("Already friends."),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Friend.DoesNotExist:
                req_dict["from_user"] = user_id
                req_dict["since"] = datetime.now().timestamp()
                friendRequestSerializer = FriendRequestSerializer(data=req_dict)
                if friendRequestSerializer.is_valid():
                    friendRequestSerializer.save()
                    # make a notification to send
                    notification = Notification(
                        noti=3,
                        user_for=req_dict["to_user"],
                        user_from=req_dict["from_user"],
                        about=0,
                        created=datetime.now().timestamp(),
                    )
                    notification.save()
                    return Response(
                        data=friendRequestSerializer.data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        friendRequestSerializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )


# Accept friend request
# -----------------------------------------------
@api_view(["PUT"])
def acceptFriendRequest(request):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id

    print(request.data)
    try:
        friend_request = FriendRequest.objects.get(id=request.data["id"])
        # Check if user responding to the request is the user request is sent to
        if friend_request.to_user == user_id:
            friendSerilizer = FriendSerializer(
                data={
                    "user_a": friend_request.from_user,
                    "user_b": user_id,
                    "since": datetime.now().timestamp(),
                }
            )
            if friendSerilizer.is_valid():
                friendSerilizer.save()
                # make a notification to send
                notification = Notification(
                    noti=4,
                    user_for=friend_request.from_user,
                    user_from=user_id,
                    about=0,
                    created=datetime.now().timestamp(),
                )
                notification.save()
                friend_request.delete()
                # Let's check if users had cross friend requested each other
                # in that case we need to delete the other request as well
                res = Response(data=friendSerilizer.data, status=status.HTTP_200_OK)
                try:
                    duplicate_request = FriendRequest.objects.get(from_user=user_id)
                    duplicate_request.delete()
                except FriendRequest.DoesNotExist:
                    return res
                return res
        return Response(
            error_response("Unable to accept friend request."),
            status=status.HTTP_400_BAD_REQUEST,
        )
    except FriendRequest.DoesNotExist:
        return Response(
            error_response("Friend request is invalid."),
            status=status.HTTP_400_BAD_REQUEST,
        )


# Log Out function, requires token
# -----------------------------------------------
@api_view(["DELETE"])
def deleteFriendRequest(request, pk):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id

    friend_request = FriendRequest.objects.get(pk=pk)
    if friend_request.from_user == user_id or friend_request.to_user == user_id:
        friend_request.delete()
        return Response(
            data=json.loads('{"action": "success"}'), status=status.HTTP_200_OK
        )
    return Response(error_response("Bad Request."), status=status.HTTP_400_BAD_REQUEST)


# Friend Suggestions for user
# -----------------------------------------------
@api_view(["GET"])
def getFriendSuggestions(request):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id

    # We have some friends
    friends = Friend.objects.filter(Q(user_a=user_id) | Q(user_b=user_id))

    # Let's add our current friends id's in list to  exclude from suggestions
    # and then excluding myself too
    friends_ids = [a.user_b if a.user_a is user_id else a.user_a for a in friends]
    friends_ids.append(user_id)

    # Apend people we have already sent friend request into friends_ids to avoid those suggestions
    try:
        freqs = FriendRequest.objects.filter(Q(from_user=user_id) | Q(to_user=user_id))
        for fr in freqs:
            if fr.to_user == user_id:
                friends_ids.append(fr.from_user)
            else:
                friends_ids.append(fr.to_user)
    except FriendRequest.DoesNotExist:
        pass

    # limiting the suggestions to 25 to prevent sending whole database
    users = list(User.objects.filter(~Q(id__in=friends_ids))[:25])
    if len(users) > 0:
        # getting 10 random ids from people we are not friends with
        # and then serializing them and returning them
        random_users_ids = [a.id for a in random.sample(users, min(len(users), 10))]
        random_users = User.objects.filter(id__in=random_users_ids)
        users_dict = [UserSerializer(user).data for user in random_users]
        return Response(
            data=dict(friend_suggestions=users_dict), status=status.HTTP_200_OK
        )
    return Response(
        error_response("No friend suggestions."), status=status.HTTP_204_NO_CONTENT
    )
