from django.urls import path

from .views import editProfile, login, logout, searchUsers, signup, userInfo

urlpatterns = [
    path("api/user/signup/", signup),
    path("api/user/login/", login),
    path("api/user/logout/", logout),
    path("api/user/edit/", editProfile),
    path("api/user/search/<query>/", searchUsers),
    path("api/user/u/<slug>/", userInfo),
]
