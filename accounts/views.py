# Create your views here.
from typing import List

from allauth.socialaccount.providers.discord.views import DiscordOAuth2Adapter  # noqa
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter  # noqa
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter  # noqa
from allauth.socialaccount.providers.oauth2.client import OAuth2Client  # noqa
from dj_rest_auth.registration.views import SocialLoginView  # noqa
from django.conf import settings


class GoogleLoginView(SocialLoginView):
    authentication_classes: List[str] = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.CALLBACK_URL  # frontend application url
    client_class = OAuth2Client


class GitHubLoginView(SocialLoginView):
    authentication_classes: List[str] = []
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.CALLBACK_URL  # frontend application url
    client_class = OAuth2Client


class DiscordLoginView(SocialLoginView):
    authentication_classes: List[str] = []
    adapter_class = DiscordOAuth2Adapter
    callback_url = settings.CALLBACK_URL  # frontend application url
    client_class = OAuth2Client
