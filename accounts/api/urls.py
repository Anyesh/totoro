# from .views import get_csrf, RefreshToken, Ping
from django.urls import path

from accounts.api.views import Ping, editProfile, get_user_info, searchUsers, signup

urlpatterns = [
    # path("api/user/get-csrf/", get_csrf),
    path("user/signup/", signup),
    path("user/ping/", Ping.as_view()),
    # path("user/refresh-token/", RefreshToken.as_view()),
    path("user/edit/", editProfile),
    path("user/search/<query>/", searchUsers),
    path("user/u/<username>/", get_user_info),
]
