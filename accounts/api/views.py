import json
from secrets import token_hex

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers import ProfileSerializer, UserSerializer
from accounts.models import Profile, User
from helpers.api_error_response import error_response
from helpers.error_messages import INVALID_REQUEST
from totoro.utils import get_response


@api_view(["GET"])
def get_user_info(request, username):
    requesting_user = request.user
    if type(requesting_user) is Response:
        return requesting_user

    try:
        data = Profile.objects.get(user__username=username)
        # user
        userSerializer = ProfileSerializer(data)
        # comments
        # comments = CommentSerializer(
        #     Comment.objects.filter(user_id=wanted_user).order_by("-pk")[:3].values(),
        #     many=True,
        # ).data
        # # posts
        # posts = Posts.objects.filter(user_id=wanted_user).order_by("pk").values()
        # posts_final = []
        # for post in posts:
        #     post_by = UserSerializer(User.objects.get(pk=post["user_id"])).data
        #     posts_final.append(
        #         {
        #             **PostsSerializer(Posts.objects.get(pk=post["id"])).data,
        #             "user": post_by,
        #         }
        #     )
        # # friends
        # try:
        #     data = Friend.objects.filter(Q(user_a=wanted_user) | Q(user_b=wanted_user))
        #     friends = [
        #         entry.user_a if entry.user_a is not wanted_user else entry.user_b
        #         for entry in data
        #     ]
        #     if friends:
        #         users = User.objects.filter(id__in=friends)
        #         users_dict = [UserSerializer(user).data for user in users]
        #         friends = users_dict
        # except Friend.DoesNotExist:
        #     friends = []

        # # isFriend: Check if user requesting this info is friends with the user
        # # we only check if wanted user and requesting user are different
        # isFriend = None
        # if requesting_user is not wanted_user:
        #     try:
        #         Friend.objects.get(
        #             Q(user_a=requesting_user) & Q(user_b=wanted_user)
        #             | Q(user_a=wanted_user) & Q(user_b=requesting_user)
        #         )
        #         isFriend = True
        #     except Friend.DoesNotExist:
        #         isFriend = False

        # # isFriendReqSent: Check if the requesting user has already sent a friend req to wanted user
        # # we only check if they are not already friends
        # isFriendReqSent = None
        # if isFriend is False:
        #     try:
        #         FriendRequest.objects.get(
        #             Q(from_user=requesting_user) & Q(to_user=wanted_user)
        #         )
        #         isFriendReqSent = True
        #     except FriendRequest.DoesNotExist:
        #         isFriendReqSent = False

        return Response(
            {
                "user_info": userSerializer.data,
                # "friends": friends,
                # "posts": posts_final,
                # "comments": comments,
                # "isFriend": isFriend,
                # "isFriendReqSent": isFriendReqSent,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    def post(self, request):
        response = Response(
            data=get_response(message="User logged out", status=True, result="Success"),
            status=status.HTTP_200_OK,
        )
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        django_logout(request)
        response.delete_cookie(settings.JWT_AUTH_COOKIE)
        response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE)

        return response


@api_view(["PUT"])
def edit_profile(request):
    user = request.user.user_id

    try:
        user_object = User.objects.get(user_id=user)
        user_object.tagline = request.data["tagline"]
        user_object.avatar = remove_prefix(request.data["avatar"], "/media")
        user_object.hometown = request.data["hometown"]
        user_object.work = request.data["work"]
        user_object.cover_image = remove_prefix(request.data["cover"], "/media")
        user_object.save()

        return Response(
            data={
                **token_response(request.headers["Authorization"].split()[-1]),
                **UserSerializer(user_object).data,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            data=error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
def search_users(request, query):
    user = request.user
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
            error_response("No search results!"), status=status.HTTP_404_NOT_FOUND
        )


def token_response(token):
    return json.loads('{"token": "' + str(token) + '"}')


def genToken():
    return token_hex(24)


def remove_prefix(text, prefix):
    if type(text) is not InMemoryUploadedFile:
        if text.startswith(prefix):
            return text[len(prefix) :]
    return text


class Ping(APIView):
    def get(self, request):
        return JsonResponse(
            {"details": f"logged in as {request.user.username}", "status_code": 200}
        )
