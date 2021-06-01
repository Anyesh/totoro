from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from accounts.models import User
from posts.models import Comment, Posts


class PostsSerializer(serializers.ModelSerializer):

    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        if obj.likes and obj.likes["users"]:
            people = []
            for user in obj.likes["users"]:
                people.append(UserSerializer(User.objects.get(pk=user)).data)
            return dict(users=people, user_ids=obj.likes["users"])

    class Meta:
        model = Posts
        fields = [
            "id",
            "user_id",
            "post_text",
            "post_image",
            "likes",
            "created",
            "updated",
        ]
        extra_kwargs = {
            "created": {"required": False},
            "updated": {"required": False},
            "post_image": {"required": False},
            "likes": {"required": False},
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post_id",
            "user_id",
            "comment_text",
            "comment_likes",
            "comment_parent",
            "created",
            "updated",
        ]
        extra_kwargs = {
            "created": {"required": False},
            "updated": {"required": False},
            "comment_likes": {"required": False},
        }
