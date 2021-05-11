import json
from datetime import datetime, timedelta
from random import randrange
from secrets import token_hex

import bcrypt
import pytz
from account.models import Token, User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from friends.models import Friend, FriendRequest
from helpers.error_messages import INVALID_REQUEST, INVALID_TOKEN, UNAUTHORIZED
from posts.api.serializers import CommentSerializer, PostsSerializer
from posts.models import Comment, Posts
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer


# Get profile info
# -----------------------------------------------
@api_view(["GET"])
def userInfo(request, slug):
    requesting_user = getUserID(request)
    if type(requesting_user) is Response:
        return requesting_user

    try:
        data = User.objects.get(slug=slug)
        wanted_user = data.id
        # user
        userSerializer = UserSerializer(data)
        # comments
        comments = CommentSerializer(
            Comment.objects.filter(user_id=wanted_user).order_by("-pk")[:3].values(),
            many=True,
        ).data
        # posts
        posts = Posts.objects.filter(user_id=wanted_user).order_by("pk").values()
        posts_final = []
        for post in posts:
            post_by = UserSerializer(User.objects.get(pk=post["user_id"])).data
            posts_final.append(
                {
                    **PostsSerializer(Posts.objects.get(pk=post["id"])).data,
                    "user": post_by,
                }
            )
        # friends
        try:
            data = Friend.objects.filter(Q(user_a=wanted_user) | Q(user_b=wanted_user))
            friends = [
                entry.user_a if entry.user_a is not wanted_user else entry.user_b
                for entry in data
            ]
            if friends:
                users = User.objects.filter(id__in=friends)
                users_dict = [UserSerializer(user).data for user in users]
                friends = users_dict
        except Friend.DoesNotExist:
            friends = []

        # isFriend: Check if user requesting this info is friends with the user
        # we only check if wanted user and requesting user are different
        isFriend = None
        if requesting_user is not wanted_user:
            try:
                Friend.objects.get(
                    Q(user_a=requesting_user) & Q(user_b=wanted_user)
                    | Q(user_a=wanted_user) & Q(user_b=requesting_user)
                )
                isFriend = True
            except Friend.DoesNotExist:
                isFriend = False

        # isFriendReqSent: Check if the requesting user has already sent a friend req to wanted user
        # we only check if they are not already friends
        isFriendReqSent = None
        if isFriend is False:
            try:
                FriendRequest.objects.get(
                    Q(from_user=requesting_user) & Q(to_user=wanted_user)
                )
                isFriendReqSent = True
            except FriendRequest.DoesNotExist:
                isFriendReqSent = False

        return Response(
            {
                "user": userSerializer.data,
                "friends": friends,
                "posts": posts_final,
                "comments": comments,
                "isFriend": isFriend,
                "isFriendReqSent": isFriendReqSent,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# Sign Up function
# -----------------------------------------------
@api_view(["POST", "PUT"])
@csrf_exempt
def signup(request):
    if request.method == "POST":
        # -- user data & hash password
        req_dict = request.data
        req_dict["password"] = hashPwd(req_dict["password"])
        req_dict["slug"] = req_dict["first_name"].lower().split()[-1] + str(
            randrange(1111, 9999)
        )
        req_dict["created"] = datetime.now().timestamp()
        req_dict["updated"] = datetime.now().timestamp()
        userSerializer = UserSerializer(data=req_dict)
        # -- check if data is without bad actors
        if UserSerializer.is_valid():
            userSerializer.save()
            # -- assign an auth token
            token = genToken()
            Token(
                token=token,
                account=User.objects.get(email=req_dict["email"]).id,
                created=datetime.now(pytz.utc),
            ).save()
            return Response(
                data={**tokenResponse(token), **userSerializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                data=userSerializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
    elif request.method == "PUT":
        user = getUserID(request)
        if type(user) is Response:
            return user

        try:
            user_object = User.objects.get(pk=user)
            user_object.tagline = request.data["tagline"]
            user_object.avatar = request.data["avatar"]
            user_object.hometown = request.data["hometown"]
            user_object.work = request.data["work"]
            user_object.save()

            token = Token.objects.get(account=user).token

            return Response(
                data={**tokenResponse(token), **UserSerializer(user_object).data},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                data=errorResponse(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
            )


# Log In function, requires email and password
# -----------------------------------------------
@api_view(["POST"])
def login(request):
    email = request.data["email"]
    password = request.data["password"]
    # -- Check if credentials are correct
    try:
        user = User.objects.get(email=email)
        if (
            bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))
            == False
        ):
            return Response(
                data=errorResponse("Credentials are invalid"),
                status=status.HTTP_403_FORBIDDEN,
            )
    except User.DoesNotExist:
        return Response(
            data=errorResponse("Credentials are invalid"),
            status=status.HTTP_403_FORBIDDEN,
        )
    # -- Assign an auth token
    try:
        token_row = Token.objects.get(account=user.id)
        token = token_row.token
        if checkIfOldToken(token_row.created):
            deleteToken(token)
            raise Token.DoesNotExist
    except Token.DoesNotExist:
        token = genToken()
        Token(token=token, account=user.id, created=datetime.now(pytz.utc)).save()
    return Response(
        data={**tokenResponse(token), **UserSerializer(user).data},
        status=status.HTTP_202_ACCEPTED,
    )


# Log Out function, requires token
# -----------------------------------------------
@api_view(["DELETE"])
def logout(request):
    token = request.headers["Authorization"].split()[-1]
    deleteToken(token)
    return Response(data=json.loads('{"action": "success"}'), status=status.HTTP_200_OK)


# Edit profile, requires token
# -----------------------------------------------
@api_view(["PUT"])
def editProfile(request):
    user = getUserID(request)
    if type(user) is Response:
        return user

    try:
        user_object = User.objects.get(pk=user)
        user_object.tagline = request.data["tagline"]
        user_object.avatar = remove_prefix(request.data["avatar"], "/media")
        user_object.hometown = request.data["hometown"]
        user_object.work = request.data["work"]
        user_object.cover_image = remove_prefix(request.data["cover"], "/media")
        user_object.save()

        return Response(
            data={
                **tokenResponse(request.headers["Authorization"].split()[-1]),
                **UserSerializer(user_object).data,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            data=errorResponse(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )


# Search people, requires token
# -----------------------------------------------
@api_view(["GET"])
def searchUsers(request, query):
    # this is keep it only accessible to logged in users
    user = getUserID(request)
    if type(user) is Response:
        return user

    query = query.replace("+", " ")
    # might not be the best solution
    query = User.objects.filter(
        Q(first_name__icontains=query.split()[0])
        | Q(last_name__icontains=query.split()[-1])
        | Q(first_name__icontains=query.split()[-1])
        | Q(last_name__icontains=query.split()[0])
    )
    results = UserSerializer(query, many=True)
    if results:
        return Response(data=results.data, status=status.HTTP_200_OK)
    else:
        return Response(
            errorResponse("No search results!"), status=status.HTTP_404_NOT_FOUND
        )


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
        return Token.objects.get(token=token).account
    except Token.DoesNotExist:
        return Response(
            errorResponse(INVALID_TOKEN), status=status.HTTP_400_BAD_REQUEST
        )


def checkIfOldToken(date):
    gap = datetime.now(tz=pytz.utc) - date
    print(gap)
    # -- If token is more than 1 day old
    if gap > timedelta(days=1):
        return True
    return False


def deleteToken(token):
    Token.objects.filter(token=token).delete()


def errorResponse(message):
    return json.loads('{"error": ["' + message + '"]}')


def tokenResponse(token):
    return json.loads('{"token": "' + str(token) + '"}')


def hashPwd(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def genToken():
    return token_hex(24)


def remove_prefix(text, prefix):
    if type(text) is not InMemoryUploadedFile:
        if text.startswith(prefix):
            return text[len(prefix) :]
    return text
