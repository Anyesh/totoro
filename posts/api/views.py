import json
from datetime import datetime

import pytz
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
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


# Get Posts of a user, Auth: not required
# -----------------------------------------------
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


# Returns only self posts of an user, Auth: REQUIRED
# -----------------------------------------------
@api_view(["GET"])
def getLoggedInUserPosts(request):
    user_id = request.user.user_id
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    return __userPosts(user_id)


# Returns self + friends posts, Auth: REQUIRED
# -----------------------------------------------
@api_view(["GET"])
def getPosts(request):
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
        friends.append(user_id)
        data = Posts.objects.filter(user_id__in=friends).order_by("pk").values()
        posts_final = []
        for post in data:
            post_by = UserSerializer(User.objects.get(pk=post["user_id"])).data
            posts_final.append(
                {
                    **PostsSerializer(Posts.objects.get(pk=post["id"])).data,
                    "user": post_by,
                }
            )
        if posts_final:
            return Response(data=posts_final, status=status.HTTP_200_OK)
        else:
            return Response(
                error_response("No posts found!"), status=status.HTTP_404_NOT_FOUND
            )
    except Friend.DoesNotExist:
        data = Posts.objects.filter(user_id=user_id)
        postsSerializer = PostsSerializer(data, many=True)
        if postsSerializer.data:
            return Response(data=postsSerializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                error_response("No posts found!"), status=status.HTTP_404_NOT_FOUND
            )


# create new post, auth required
# -----------------------------------------------
@api_view(["POST"])
def newPost(request):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    if request.data["post_image"] != "null":
        print(request.data["post_image"])
        req_data = {
            "post_text": request.data["post_text"],
            "post_image": request.data["post_image"],
        }
    else:
        req_data = {"post_text": request.data["post_text"]}
    time_stamp = datetime.now().timestamp()
    postsSerializer = PostsSerializer(
        data={
            **req_data,
            **{"user_id": user_id, "created": time_stamp, "updated": time_stamp},
        }
    )
    if postsSerializer.is_valid():
        postsSerializer.save()
        return Response(data=postsSerializer.data, status=status.HTTP_201_CREATED)
    return Response(postsSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# For operations on one singular post, Auth: REQUIRED
# @url: api/post/<int:pk>
# -----------------------------------------------
@api_view(["GET", "DELETE", "PUT", "POST"])
@csrf_exempt
def postOperations(request, pk):
    if request.method == "GET":
        return getPost(pk)
    elif request.method == "PUT":
        return likePost(request, pk)
    elif request.method == "POST":
        return editPost(request, pk)
    elif request.method == "DELETE":
        return deletePost(request, pk)
    return Response(
        error_response("unable to complete request"),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# Get one specific post, Auth: not required
# -----------------------------------------------
def getPost(post_key):
    try:
        data = Posts.objects.get(pk=post_key)
        post_by = UserSerializer(User.objects.get(pk=data.user_id)).data
        return Response(
            data={
                **PostsSerializer(Posts.objects.get(pk=data.id)).data,
                "user": post_by,
            },
            status=status.HTTP_200_OK,
        )
    except Posts.DoesNotExist:
        return Response(
            error_response("Post not found!"), status=status.HTTP_404_NOT_FOUND
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
