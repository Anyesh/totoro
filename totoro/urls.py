"""totoro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from typing import List

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# from django.urls.conf import re_path
from django.urls.resolvers import URLResolver

api_urls: List[URLResolver] = [
    path("social/", include("accounts.urls")),
    # path("auth/", include("dj_rest_auth.urls")),
    path("", include("accounts.api.urls")),
    path("", include("posts.api.urls")),
    path("", include("friends.api.urls")),
    path("", include("notifications.api.urls")),
]

admin_url: List[URLResolver] = [
    path("admin/", admin.site.urls),
]

urlpatterns: List[URLResolver] = [
    path("api/", include(api_urls)),
    # re_path(r"^accounts/", include("allauth.urls"), name="socialaccount_signup"),
    *admin_url,
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),  # type: ignore
]

# if settings.DEBUG:
#     urlpatterns += [
#         path("dev/auth/", include("dj_rest_auth.urls")),
#     ]
