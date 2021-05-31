# Create your views here.
from typing import List

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings


class GoogleLoginView(SocialLoginView):
    authentication_classes: List[str] = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.CALLBACK_URL  # frontend application url
    client_class = OAuth2Client
