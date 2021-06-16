from django.urls import path

from .views import AddNewPost, Posts, UserPosts
from .views_comments import actionsComment, getPostComments, postNewComment

urlpatterns = [
    path("user/<str:user_id>/posts/", UserPosts.as_view()),
    path("user/posts/", UserPosts.as_view()),
    path("post/new/", AddNewPost),
    path("post/<int:post_id>/", Posts.as_view()),
    path("post/all/", Posts.as_view()),
    path("<int:post>/comments/", getPostComments),
    path("<int:post_id>/comments/new/", postNewComment),
    path("<int:post_id>/comments/<int:pk>/", actionsComment),
]
