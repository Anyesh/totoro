from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from accounts.models import User
from posts.models import RESIZE_THRESH, Comment, Post


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "image", "author"]

    # def update(self, validated_data):
    #     return Post.objects.update(**validated_data)

    # def create(self, validated_data):
    #     instance = Post.objects.create(**validated_data)
    #     instance.is_published = True
    #     instance.save()
    #     # if self.context.get('tags'):
    #     #     for user in self.context.get('tags'):
    #     #         instance.tags.add(user)
    #     #         instance.save()
    #     return instance


class PostSerializer(serializers.ModelSerializer):

    likes = serializers.SerializerMethodField()
    src = serializers.SerializerMethodField()
    _author = serializers.SerializerMethodField()

    def get__author(self, obj):

        return {
            "user_id": obj.author.user_id,
            "username": obj.author.username,
            "email": obj.author.email,
            "avatar": obj.author.profile.avatar,
        }

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
            "placeholder": {
                "url": obj.placeholder,
                "height": obj.height,
                "width": obj.width,
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
        model = Post
        fields = [
            "id",
            "title",
            "_author",
            "src",
            "categories",
            "likes",
            "is_published",
            "created_at",
            "updated_at",
        ]


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
