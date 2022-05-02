import json
from secrets import token_hex

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.api.serializers import ProfileSerializer, UserSerializer
from accounts.models import User
from helpers.api_error_response import error_response
from helpers.error_messages import INVALID_REQUEST
from totoro.utils import get_response


class LogoutView(APIView):
    def logout(self, request):
        response = Response(
            data=get_response(message="User logged out", status=True, result="Success"),
            status=status.HTTP_200_OK,
        )

        try:
            refresh_token = request.data["refresh_token"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, KeyError) as e:
            return Response(
                data=get_response(
                    message=f"Invalid token! {e}", status=False, result="Error"
                ),
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        django_logout(request)
        response.delete_cookie(settings.JWT_AUTH_COOKIE)
        response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE)
        return response

    def post(self, request):
        return self.logout(request)


@api_view(["PUT"])
def edit_profile(request):
    user = request.user.user_id

    try:
        user_object = User.objects.get(user_id=user)
        user_object.tagline = request.data["tagline"]
        user_object.avatar = remove_prefix(request.data["avatar"], "/media")
        user_object.hometown = request.data["hometown"]
        user_object.work = request.data["work"]
        user_object.cover_image = remove_prefix(request.data["cover"], "/media")
        user_object.save()

        return Response(
            data={
                **token_response(request.headers["Authorization"].split()[-1]),
                **UserSerializer(user_object).data,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            data=error_response(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
def search_users(request, query):
    query = query.replace("+", " ")
    # might not be the best solution
    query = User.objects.filter(
        Q(first_name__icontains=query.split()[0])
        | Q(last_name__icontains=query.split()[-1])
        | Q(first_name__icontains=query.split()[-1])
        | Q(last_name__icontains=query.split()[0])
    )
    if results := UserSerializer(query, many=True):
        return Response(data=results.data, status=status.HTTP_200_OK)
    else:
        return Response(
            error_response("No search results!"), status=status.HTTP_404_NOT_FOUND
        )


def token_response(token):
    return json.loads('{"token": "' + str(token) + '"}')


def genToken():
    return token_hex(24)


def remove_prefix(text, prefix):
    if type(text) is not InMemoryUploadedFile and text.startswith(prefix):
        return text[len(prefix) :]
    return text


class Ping(APIView):
    @method_decorator(cache_page(settings.CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request):

        serializer = ProfileSerializer(request.user.profile)

        return JsonResponse(
            data=get_response(
                message="Ping was a success!",
                result={"data": serializer.data},
                status=True,
                status_code=200,
            ),
            status=status.HTTP_200_OK,
        )
