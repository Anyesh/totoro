import json
from datetime import datetime

import pytz
from django.db.models import Q
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from friends.models import Friend
from helpers.api_error_response import error_response
from helpers.error_messages import UNAUTHORIZED
from notifications.models import Notification
from posts.api.serializers import PostCreateSerializer, PostSerializer
from posts.models import Comment, Post
from totoro.utils import get_response


@api_view(["GET"])
def UserSpecificPosts(request, user_id):
    return __userPosts(user_id)


def __userPosts(user_id):
    data = Post.objects.filter(user_id=user_id)
    postsSerializer = PostSerializer(data, many=True)
    if postsSerializer.data:
        return Response(data=postsSerializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            error_response("No posts found!"), status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
def LoggedInUserPosts(request):
    user_id = request.user.user_id
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    return __userPosts(user_id)


class PostsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        if not data:
            return JsonResponse(
                data=get_response(
                    message="Post could not be retrieved!",
                    status_code=404,
                    status=False,
                    result={"data": data},
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        return JsonResponse(
            data=get_response(
                message="Post retrieved succesfully!",
                status_code=200,
                status=True,
                result={
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": self.page.paginator.count,
                    "data": data,
                },
            ),
            status=status.HTTP_200_OK,
        )


class Posts(APIView):
    pagination_class = PostsPagination
    serializer_class = PostSerializer

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get_queryset(self, request, post_id):
        if post_id:
            return Post.objects.filter(pk=post_id)

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
        return Post.objects.filter(author_id__in=friends).order_by("pk")

    def get(self, request, post_id=None):

        page = self.paginate_queryset(self.get_queryset(request, post_id))
        if page is not None:
            serializer = self.serializer_class(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)


@api_view(["POST"])
def AddNewPost(request):
    user = request.user.user_id

    req_data = {
        "title": request.data.get("title"),
        "image": request.data.get("image"),
    }

    serializer = PostCreateSerializer(
        data={
            **req_data,
            **{"author": user},
        },
    )
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(
            data=get_response(
                message="Post created succesfully.",
                result={"data": serializer.data},
                status=True,
                status_code=201,
            ),
            status=status.HTTP_201_CREATED,
        )
    return JsonResponse(
        data=get_response(
            message="There was an error.",
            result=serializer.errors,
            status=True,
            status_code=400,
        ),
        status=status.HTTP_400_BAD_REQUEST,
    )


def likePost(request, post_key):
    user_id = request.user
    # If user_id type is Response that means we have errored
    if type(user_id) is Response:
        return user_id
    post = Post.objects.get(pk=post_key)
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
    post = Post.objects.get(pk=post_key)
    if post.user == user_id:
        post.post_text = request.data["post_text"]
        post.post_image = request.data["post_image"]
        post.updated = datetime.now(tz=pytz.utc)
        post.save()
        return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
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
    post = Post.objects.get(pk=post_key)
    if post.user_id != user_id:
        return Response(
            error_response(UNAUTHORIZED), status=status.HTTP_401_UNAUTHORIZED
        )

    post.delete()
    Comment.objects.filter(post_id=post.id).delete()
    return Response(json.loads('{"action":"success"}'), status=status.HTTP_200_OK)
