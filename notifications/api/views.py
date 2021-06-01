import datetime
import json

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.api.serializers import UserSerializer
from accounts.models import Token, User
from helpers.api_error_response import errorResponse
from helpers.error_messages import INVALID_REQUEST, INVALID_TOKEN, UNAUTHORIZED
from notifications.models import Notification

# seen [0:not-seen, 1:seen]
# noti: notification type [0: like, 1: comment, 2: new post, 3: friend req]
# about [0: post, 1: friend]


@api_view(["GET"])
def getNotifications(request):
    user_id = getUserID(request)
    if type(user_id) is Response:
        return user_id

    # Get notifications which are at most a day old; or are not seen yet unrelated to time
    notifications = (
        Notification.objects.filter(user_for=user_id)
        .filter(
            Q(seen=0)
            | Q(
                created__range=(
                    (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp(),
                    datetime.datetime.now().timestamp(),
                )
            )
        )
        .values()
    )
    res = []
    for notif in notifications:
        user_by = UserSerializer(User.objects.get(pk=notif["user_from"])).data
        res.append({**notif, **{"user": user_by}})
    return Response(data=res, status=status.HTTP_200_OK)


@api_view(["PUT"])
def markAsSeen(request, pk):
    user_id = getUserID(request)
    if type(user_id) is Response:
        return user_id

    try:
        notification = Notification.objects.get(pk=pk)
        notification.seen = 1
        notification.save()
        return Response(json.loads('{"action":"success"}'), status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response(
            errorResponse(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
def markAllAsSeen(request):
    user_id = getUserID(request)
    if type(user_id) is Response:
        return user_id

    unseen_notifications = Notification.objects.filter(seen=0).values()
    for notification in unseen_notifications:
        notification = Notification.objects.get(pk=notification["id"])
        notification.seen = 1
        notification.save()
    return Response(json.loads('{"action":"success"}'), status=status.HTTP_200_OK)


# Helper Functions
# -----------------------------------------------
def getUserID(request):
    try:
        token = request.headers["Authorization"].split()[-1]
    except KeyError:
        return Response(
            errorResponse(UNAUTHORIZED), status=status.HTTP_401_UNAUTHORIZED
        )
    try:
        return Token.objects.get(token=token).accounts
    except Token.DoesNotExist:
        return Response(
            errorResponse(INVALID_TOKEN), status=status.HTTP_400_BAD_REQUEST
        )
