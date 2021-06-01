from django.urls import path

from .views import DiscordLoginView, GitHubLoginView, GoogleLoginView

urlpatterns = [
    path("google/", GoogleLoginView.as_view(), name="google"),
    path("github/", GitHubLoginView.as_view(), name="github"),
    path("discord/", DiscordLoginView.as_view(), name="discord"),
]
