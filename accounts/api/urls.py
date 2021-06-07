# from .views import get_csrf, RefreshToken, Ping
from dj_rest_auth.jwt_auth import get_refresh_view
from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from accounts.api.views import (
    LogoutView,
    Ping,
    edit_profile,
    get_user_info,
    search_users,
)

urlpatterns = [
    # path("api/user/get-csrf/", get_csrf),
    path("user/ping/", Ping.as_view()),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/token/verify/", TokenVerifyView().as_view(), name="token_verify"),
    path("auth/token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    path("user/edit/", edit_profile),
    path("user/search/<query>/", search_users),
    path("user/u/<username>/", get_user_info),
]
