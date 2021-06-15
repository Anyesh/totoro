from django.urls import path

from .views import AddNewPost, LoggedInUserPosts, Posts, UserSpecificPosts
from .views_comments import actionsComment, getPostComments, postNewComment

urlpatterns = [
    path("user/<int:user_id>/posts/", UserSpecificPosts),
    path("user/posts/", LoggedInUserPosts),
    path("post/new/", AddNewPost),
    path("post/<int:post_id>/", Posts.as_view()),
    path("post/all/", Posts.as_view()),
    path("<int:post>/comments/", getPostComments),
    path("<int:post_id>/comments/new/", postNewComment),
    path("<int:post_id>/comments/<int:pk>/", actionsComment),
]
