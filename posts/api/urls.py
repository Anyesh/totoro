from django.urls import path

from .views import get_post, get_posts, getLoggedInUserPosts, new_post, userPosts
from .views_comments import actionsComment, getPostComments, postNewComment

urlpatterns = [
    path("user/<int:pk>/posts/", userPosts),
    path("user/posts/", getLoggedInUserPosts),
    path("post/new/", new_post),
    path("post/<int:pk>/", get_post),
    path("posts/", get_posts),
    path("<int:post>/comments/", getPostComments),
    path("<int:post_id>/comments/new/", postNewComment),
    path("<int:post_id>/comments/<int:pk>/", actionsComment),
]
