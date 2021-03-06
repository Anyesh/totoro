import json
from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.api.serializers import UserSerializer
from accounts.models import User
from friends.models import Friend
from helpers.api_error_response import error_response
from helpers.error_messages import INVALID_REQUEST
from notifications.models import Notification
from posts.models import Comment, Post

from .serializers import CommentSerializer


# Get all post comments
# By default it requires user to be logged in and be friends with post author
@api_view(["GET"])
def getPostComments(request, post):
    user = request.user
    if type(user) is Response:
        return user

    author = getAuthor(post)
    if type(author) is Response:
        return author

    if isFriends(author.user_id, user) or author.user_id == user:
        # User can only retrieve comments if they are friends with author or author themselves
        result = [
            {
                **comment,
                "user": UserSerializer(
                    User.objects.get(user_id=comment["user_id"])
                ).data,
            }
            for comment in Comment.objects.filter(post_id=post).order_by("pk").values()
        ]
        return Response({"comments": result}, status=status.HTTP_200_OK)

    return Response(error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST)


# Post a new comment on a post
# Requires commentator to be friends with post author
# ---------------------------------------------------
@api_view(["POST"])
def postNewComment(request, post_id):
    user = request.user
    if type(user) is Response:
        return user

    post = getPost(post_id)
    if type(post) is Response:
        return post
    time_stamp = datetime.now().timestamp()

    # Filtering
    if post.user_id != user and not isFriends(post.user_id, user):
        # post author and user trying to comment are not friends
        # if they are friends then we let the commentator post a comment
        return Response(
            error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )

    commentSerializer = CommentSerializer(
        data={
            "post_id": post.id,
            "user_id": user,
            "comment_text": request.data["comment_text"],
            "comment_parent": request.data["comment_parent"],
            "created": time_stamp,
            "updated": time_stamp,
        }
    )
    if commentSerializer.is_valid():
        commentSerializer.save()
        try:
            # make a notification to send
            p_for = (
                post.user_id
                if request.data["comment_parent"] == "0"
                else Comment.objects.get(pk=int(request.data["comment_parent"])).user_id
            )
            if p_for != user:
                notification = Notification(
                    noti=1 if request.data["comment_parent"] == "0" else 5,
                    user_for=p_for,
                    user_from=user,
                    about=post.id,
                    created=datetime.now().timestamp(),
                )
                notification.save()
        except Comment.DoesNotExist:
            print("errored")
        return Response(
            data={
                **commentSerializer.data,
                "user": UserSerializer(User.objects.get(user_id=user)).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(commentSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Actions on a comment
# Requires Auth
# ---------------------------------------------------
@api_view(["PUT", "DELETE", "POST"])
def actionsComment(request, post_id, pk):
    user_id = request.user
    if type(user_id) is Response:
        return user_id

    if request.method == "PUT":
        # Liking a comment
        comment = Comment.objects.get(pk=pk)
        if comment.comment_likes:
            if user_id in comment.comment_likes["users"]:
                comment.comment_likes["users"].remove(user_id)
            else:
                comment.comment_likes["users"].append(user_id)
        else:
            comment.comment_likes = dict(users=[(user_id)])
        comment.save()
        # make a notification to send
        if comment.user_id != user_id:
            notification = Notification(
                noti=2,
                user_for=comment.user_id,
                user_from=user_id,
                about=comment.post_id,
                created=datetime.now().timestamp(),
            )
            notification.save()
        return Response(json.loads('{"action":"success"}'), status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        try:
            comment = Comment.objects.get(pk=pk)
            if comment.user_id == user_id:
                comment.delete()
                return Response(
                    json.loads('{"action":"success"}'), status=status.HTTP_200_OK
                )
        except Comment.DoesNotExist:
            return Response(
                error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
            )

    return Response(error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST)


# Helper Functions
# # *********************************************
# def (request.user):
#     try:
#         token = request.headers["Authorization"].split()[-1]
#     except KeyError:
#         return Response(
#             error_response(UNAUTHORIZED), status=status.HTTP_401_UNAUTHORIZED
#         )
#     try:
#         return Token.objects.get(token=token).accounts
#     except Token.DoesNotExist:
#         return Response(
#             error_response(INVALID_TOKEN), status=status.HTTP_400_BAD_REQUEST
#         )


def isFriends(user_a, user_b):
    try:
        Friend.objects.get(
            Q(user_a=user_a) & Q(user_b=user_b) | Q(user_a=user_b) & Q(user_b=user_a)
        )
        return True
    except Friend.DoesNotExist:
        return False


def getAuthor(post):
    # getAuthor returns a user model
    try:
        post_author_id = Post.objects.get(id=post).user_id
        try:
            return User.objects.get(user_id=post_author_id)
        except User.DoesNotExist:
            return Response(
                error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
            )
    except Post.DoesNotExist:
        return Response(
            error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )


def getPost(post):
    try:
        return Post.objects.get(id=post)
    except Post.DoesNotExist:
        return Response(
            error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )
