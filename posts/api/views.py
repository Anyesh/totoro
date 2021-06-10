import json
from datetime import datetime

import pytz
from django.db.models import Q
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.api.serializers import UserSerializer
from accounts.models import User
from friends.models import Friend
from helpers.api_error_response import error_response
from helpers.error_messages import UNAUTHORIZED
from notifications.models import Notification
from posts.api.serializers import PostsSerializer
from posts.models import Comment, Posts
from totoro.utils import get_response


@api_view(["GET"])
def userPosts(request, pk):
    return __userPosts(pk)


def __userPosts(pk):
    user_id = pk
    data = Posts.objects.filter(user_id=user_id)
    postsSerializer = PostsSerializer(data, many=True)
    if postsSerializer.data:
        return Response(data=postsSerializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            error_response("No posts found!"), status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
def getLoggedInUserPosts(request):
    user_id = request.user.user_id
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    return __userPosts(user_id)


@api_view(["GET"])
def get_posts(request):
    user_id = request.user.user_id
    friends = []

    data = Friend.objects.filter(Q(user_a=user_id) | Q(user_b=user_id))
    if data:
        friends = [
            entry.user_a if entry.user_a is not user_id else entry.user_b
            for entry in data
        ]
        friends.append(user_id)
    else:
        friends = [user_id]
    data = Posts.objects.filter(author_id__in=friends).order_by("pk").values()
    posts_final = []
    for post in data:
        author = UserSerializer(User.objects.get(pk=post["author_id"])).data
        posts_final.append(
            {
                **PostsSerializer(
                    Posts.objects.get(pk=post["id"]), context={"request": request}
                ).data,
                "author": author,
            }
        )

    return JsonResponse(
        data=get_response(
            message="Posts retrieved succesfully!",
            status_code=200,
            status=True,
            result={"data": posts_final},
        ),
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def new_post(request):
    user = request.user.user_id
    print(request.data)

    req_data = {
        "title": request.data.get("title"),
        "image": request.data.get("image"),
    }

    postsSerializer = PostsSerializer(
        data={
            **req_data,
            **{"author": user},
        },
        context={"request": request},
    )
    if postsSerializer.is_valid():
        postsSerializer.save()
        return JsonResponse(
            data=get_response(
                message="Post created succesfully.",
                result={"data": postsSerializer.data},
                status=True,
                status_code=201,
            ),
            status=status.HTTP_201_CREATED,
        )
    return JsonResponse(
        data=get_response(
            message="There was an error.",
            result=postsSerializer.errors,
            status=True,
            status_code=400,
        ),
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def get_post(request, pk):
    try:
        data = Posts.objects.get(pk=pk)

        return JsonResponse(
            data=get_response(
                message="Posts retrieved succesfully!",
                status_code=200,
                status=True,
                result={
                    "data": PostsSerializer(
                        Posts.objects.get(pk=data.id), context={"request": request}
                    ).data
                },
            ),
            status=status.HTTP_200_OK,
        )
    except Posts.DoesNotExist:
        return JsonResponse(
            data=get_response(
                message="Post with given id not found!",
                status_code=404,
                status=False,
                result={"data": []},
            ),
            status=status.HTTP_404_NOT_FOUND,
        )


# Like or unlike a post, Auth: REQUIRED
# -----------------------------------------------
def likePost(request, post_key):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    post = Posts.objects.get(pk=post_key)
    if post.likes:
        if user_id in post.likes["users"]:
            post.likes["users"].remove(user_id)
            isLiked = False
        else:
            post.likes["users"].append(user_id)
            isLiked = True
    else:
        post.likes = dict(users=[(user_id)])
        isLiked = True
    post.save()
    # make a notification to send
    if post.user_id != user_id and isLiked:
        notification = Notification(
            noti=0,
            user_for=post.user_id,
            user_from=user_id,
            about=post.id,
            created=datetime.now().timestamp(),
        )
        notification.save()
    return Response(json.loads('{"action":"success"}'), status=status.HTTP_200_OK)


# Edit a post, Auth: REQUIRED
# @required in request: post_text, post_image
# -----------------------------------------------
def editPost(request, post_key):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    post = Posts.objects.get(pk=post_key)
    if post.user == user_id:
        post.post_text = request.data["post_text"]
        post.post_image = request.data["post_image"]
        post.updated = datetime.now(tz=pytz.utc)
        post.save()
        return Response(PostsSerializer(post).data, status=status.HTTP_200_OK)
    else:
        return Response(
            error_response(UNAUTHORIZED), status=status.HTTP_401_UNAUTHORIZED
        )


# delete a post, Auth: REQUIRED
# -----------------------------------------------
def deletePost(request, post_key):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    post = Posts.objects.get(pk=post_key)
    if post.user_id == user_id:
        post.delete()
        Comment.objects.filter(post_id=post.id).delete()
        return Response(json.loads('{"action":"success"}'), status=status.HTTP_200_OK)
    else:
        return Response(
            error_response(UNAUTHORIZED), status=status.HTTP_401_UNAUTHORIZED
        )
