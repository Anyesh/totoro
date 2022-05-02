# Create your views here.
import hashlib
from typing import List, Optional

from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.providers.discord.views import DiscordOAuth2Adapter  # noqa
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter  # noqa
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter  # noqa
from allauth.socialaccount.providers.oauth2.client import OAuth2Client  # noqa
from dj_rest_auth.registration.views import SocialLoginView  # noqa
from django.conf import settings

from accounts.models import Profile, User
from totoro.utils import get_client_ip


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


def create_user_profile(user: User, sociallogin: Optional[SocialLogin] = None):

    preferred_avatar_size_pixels = 256
    ip = None
    picture_url = "http://www.gravatar.com/avatar/{0}?s={1}".format(
        hashlib.md5(user.email.encode("UTF-8")).hexdigest(),
        preferred_avatar_size_pixels,
    )
    f_name = None
    l_name = None
    work = None
    tagline = None
    hometown = None

    def handle_discord(social_account):
        f_name = social_account.extra_data.get("given_name")
        l_name = social_account.extra_data.get("family_name")
        picture_url = (
            "https://cdn.discordapp.com/avatars"
            f"/{social_account.extra_data.get('id')}"
            f"/{social_account.extra_data.get('avatar')}.png"
        )
        return f_name, l_name, picture_url

    def handle_google(social_account):
        f_name = social_account.extra_data.get("given_name")
        l_name = social_account.extra_data.get("family_name")

        # verified = social_account.extra_data['verified_email']
        picture_url = social_account.extra_data.get("picture")
        return f_name, l_name, picture_url

    def handle_github(social_account):
        f_name = None
        l_name = None
        if name := social_account.extra_data.get("name"):
            f_name, l_name = name.split(" ")
        tagline = social_account.extra_data.get("bio")
        work = social_account.extra_data.get("company")
        hometown = social_account.extra_data.get("location")

        picture_url = social_account.extra_data.get("avatar_url")
        return f_name, l_name, tagline, work, hometown, picture_url

    if not sociallogin:
        social_account = SocialAccount.objects.filter(user=user.user_id).first()
        if not social_account:  # user has no social account
            Profile.objects.update_or_create(user=user)
            return True
    else:
        social_account = sociallogin.account
        if not social_account:
            return False
        ip = get_client_ip()

    if social_account.provider == "discord":
        f_name, l_name, picture_url = handle_discord(social_account)
    if social_account.provider == "google":
        f_name, l_name, picture_url = handle_google(social_account)
    if social_account.provider == "github":
        f_name, l_name, tagline, work, hometown, picture_url = handle_github(
            social_account
        )

    ip = get_client_ip()
    obj, created = Profile.objects.update_or_create(
        user=user,
        current_ip=ip,
        avatar=picture_url,
        first_name=f_name,
        last_name=l_name,
        work=work,
        hometown=hometown,
        tagline=tagline,
    )

    return True
