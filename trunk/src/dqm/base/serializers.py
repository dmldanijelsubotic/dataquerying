from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Tag


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `include` argument that
    controls which fields should be displayed.
    """

    include_set = {"tags", "user", "posts", "comments"}

    def __init__(self, *args, **kwargs):
        include = kwargs.pop("include", None)

        super().__init__(*args, **kwargs)

        if include is not None:
            # Do not exclude any fields that are specified in the `include` argument.
            allowed = self.include_set.intersection(set(include))
            existing = set(self.fields).intersection(self.include_set)

            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

    def validate_name(self, value):
        if Tag.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A tag with this name already exists.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "text", "user", "post", "created_at", "updated_at"]


class PostSerializer(DynamicFieldsModelSerializer):
    user = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "status",
            "user",
            "tags",
            "comments",
            "created_at",
            "updated_at",
        ]


class UserDetailSerializer(DynamicFieldsModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "posts",
            "comments",
        ]
