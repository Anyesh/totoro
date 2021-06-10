from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from accounts.models import User
from posts.models import RESIZE_THRESH, Comment, Posts


class PostsSerializer(serializers.ModelSerializer):

    likes = serializers.SerializerMethodField()
    src = serializers.SerializerMethodField()

    def get_src(self, obj):
        request = self.context.get("request")
        return {
            "original": {
                "url": request.build_absolute_uri(obj.image.url),
                "height": obj.height,
                "width": obj.width,
            },
            "thumbnail": {
                "url": request.build_absolute_uri(obj.thumbnail.url),
                "height": int(obj.height * RESIZE_THRESH),
                "width": int(obj.width * RESIZE_THRESH),
            },
        }

    def get_likes(self, obj):
        if obj.likes and obj.likes.get("users"):
            people = [
                UserSerializer(User.objects.get(user_id=user)).data
                for user in obj.likes["users"]
            ]

            return dict(users=people, user_ids=obj.likes.get("users"))

    class Meta:
        model = Posts
        fields = [
            "id",
            "title",
            "image",
            "categories",
            "title",
            "likes",
            "created_at",
            "updated_at",
            "height",
            "width",
            "author",
            "src",
        ]
        extra_kwargs = {
            "created_at": {"required": False},
            "height": {"required": False},
            "width": {"required": False},
            "categories": {"required": False},
            "src": {"required": False},
            "updated_at": {"required": False},
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
