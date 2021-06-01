from django.urls import path

from .views import getLoggedInUserPosts, getPosts, newPost, postOperations, userPosts
from .views_comments import actionsComment, getPostComments, postNewComment

urlpatterns = [
    path("user/<int:pk>/posts/", userPosts),
    path("user/posts/", getLoggedInUserPosts),
    path("post/new/", newPost),
    path("post/<int:pk>/", postOperations),
    path("posts/", getPosts),
    path("<int:post>/comments/", getPostComments),
    path("<int:post_id>/comments/new/", postNewComment),
    path("<int:post_id>/comments/<int:pk>/", actionsComment),
]
