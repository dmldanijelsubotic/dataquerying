from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, UserDetailSet, TagViewSet, CommentViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"posts", PostViewSet, basename="post")
router.register(r"users", UserDetailSet, basename="user")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
