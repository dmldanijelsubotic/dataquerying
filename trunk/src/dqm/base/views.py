from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .filters import PostFilter
from .models import Post, Tag, Comment
from .serializers import (
    PostSerializer,
    TagSerializer,
    CommentSerializer,
    UserDetailSerializer,
)
from .mixins import AddIncludeQueryParam, ViewSetAddUser


class PostViewSet(AddIncludeQueryParam, ViewSetAddUser, viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter
    # permission_classes = [IsAuthenticated]


class UserDetailSet(AddIncludeQueryParam, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    # permission_classes = [IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = [IsAuthenticated]


class CommentViewSet(ViewSetAddUser, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]
