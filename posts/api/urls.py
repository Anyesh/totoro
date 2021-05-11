from django.urls import path

from .views import getLoggedInUserPosts, getPosts, newPost, postOperations, userPosts
from .views_comments import actionsComment, getPostComments, postNewComment

urlpatterns = [
    path("api/user/<int:pk>/posts/", userPosts),  # if we have a user id
    path("api/user/posts/", getLoggedInUserPosts),  # posts of logged in user
    path("api/post/new/", newPost),
    path(
        "api/post/<int:pk>/", postOperations
    ),  # get, need auth any TODO: friend # put, need auth any # post, need auth author # delete, need auth author
    path("api/posts/", getPosts),
    # Comments
    path("api/<int:post>/comments/", getPostComments),
    path("api/<int:post_id>/comments/new/", postNewComment),
    path(
        "api/<int:post_id>/comments/<int:pk>/", actionsComment
    ),  # like(PUT), update(POST), delete (DELETE) a comment
]
