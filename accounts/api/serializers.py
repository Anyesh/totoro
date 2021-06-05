from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Gender, Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"],
        )

        return user


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ["title"]


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    gender = GenderSerializer()

    class Meta:
        model = Profile
        fields = [
            "user",
            "first_name",
            "last_name",
            "gender",
            "email",
            "avatar",
            "birthday",
            "tagline",
            "created",
            "updated",
            "hometown",
            "work",
            "cover_image",
        ]
        # extra_kwargs = {
        #     "password": {"write_only": True},
        #     "email": {"write_only": True},

        #     "created": {"required": False},
        #     "updated": {"required": False},
        #     "birthday": {"required": False},
        #     "avatar": {"required": False},
        #     "tagline": {"required": False},
        #     "hometown": {"required": False},
        #     "work": {"required": False},
        #     "cover_image": {"required": False},
        # }


class TotoroTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username

        return token


class TotoroTokenObtainPairView(TokenObtainPairView):
    serializer_class = TotoroTokenObtainPairSerializer
