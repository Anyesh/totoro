from django.urls import path

# from .views import get_csrf, RefreshToken, Ping
from .views import (LoginView, editProfile, logout, searchUsers, signup,
                    userInfo)

urlpatterns = [
    # path("api/user/get-csrf/", get_csrf),
    path("api/user/signup/", signup),
    path("api/user/login/", LoginView),
    # path("api/user/ping/", Ping.as_view()),
    # path("api/user/refresh-token/", RefreshToken.as_view()),
    path("api/user/logout/", logout),
    path("api/user/edit/", editProfile),
    path("api/user/search/<query>/", searchUsers),
    path("api/user/u/<slug>/", userInfo),
]
