from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import resolve

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.serializers import ValidationError

from .models import Tag, Post, Comment
from .serializers import PostSerializer, TagSerializer
from .filters import PostFilter
from .views import PostViewSet, UserDetailSet


class ModelTest(TestCase):
    """Test Model creation and string representation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.tag = Tag.objects.create(name="Django")
        self.post = Post.objects.create(
            title="Test Post",
            content="Content here",
            status=Post.StatusChoices.PUBLISHED,
            user=self.user,
        )
        self.post.tags.add(self.tag)
        self.comment = Comment.objects.create(
            text="Great post!", post=self.post, user=self.user
        )

    def test_tag_creation_and_str(self):
        self.assertEqual(self.tag.name, "Django")
        self.assertEqual(str(self.tag), "Django")

    def test_post_creation_and_str(self):
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.status, "pblsh")
        self.assertIn(self.tag, self.post.tags.all())
        self.assertEqual(str(self.post), "Test Post")
        self.assertEqual(Post.StatusChoices.DRAFT, "draft")
        self.assertEqual(Post.StatusChoices.PUBLISHED, "pblsh")

    def test_comment_creation_and_str(self):
        self.assertEqual(self.comment.text, "Great post!")
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(str(self.comment), f"Comment {self.post} by {self.user}")


class SerializerTest(TestCase):
    """Test Serializer functionalities including dynamic fields and validation."""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw")
        self.post = Post.objects.create(
            title="Dynamic Post",
            content="Test",
            user=self.user,
            status=Post.StatusChoices.DRAFT,
        )
        Tag.objects.create(name="existing tag")

    def test_post_serializer_full_fields(self):
        """Test PostSerializer output when no dynamic fields are excluded."""
        serializer = PostSerializer(instance=self.post)
        fields = list(serializer.data.keys())
        expected_fields = [
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
        self.assertCountEqual(fields, expected_fields)

    def test_post_serializer_dynamic_fields_include(self):
        """Test PostSerializer with the 'include' argument to restrict nested fields."""
        serializer = PostSerializer(instance=self.post, include=["user", "tags"])
        fields = list(serializer.data.keys())

        self.assertIn("user", fields)
        self.assertIn("tags", fields)

        self.assertNotIn("comments", fields)

        self.assertIn("title", fields)

    def test_tag_serializer_name_unique_validation(self):
        """Test case-insensitive unique validation for Tag name."""
        serializer = TagSerializer(data={"name": "Existing Tag"})  # Different case
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)

        self.assertIn(
            "A tag with this name already exists.", cm.exception.detail["name"]
        )


class PostFilterTest(TestCase):
    """Test PostFilter functionality, especially the date range filters."""

    def setUp(self):
        self.user = User.objects.create_user(username="filer", password="pw")

        now = timezone.now()

        self.post_old = Post.objects.create(
            title="Old Post",
            content="Content",
            user=self.user,
            status=Post.StatusChoices.PUBLISHED,
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=30),
        )
        self.post_mid = Post.objects.create(
            title="Mid Post",
            content="Content",
            user=self.user,
            status=Post.StatusChoices.DRAFT,
            created_at=now - timedelta(days=15),
            updated_at=now - timedelta(days=15),
        )
        self.post_new = Post.objects.create(
            title="New Post",
            content="Content",
            user=self.user,
            status=Post.StatusChoices.PUBLISHED,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        )

        self.queryset = Post.objects.all()

    def test_status_filter_exact(self):
        filtered_qs = PostFilter(
            {"status": Post.StatusChoices.PUBLISHED}, queryset=self.queryset
        ).qs
        self.assertIn(self.post_old, filtered_qs)
        self.assertIn(self.post_new, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)


class DRFIntegrationTest(APITestCase):
    """Test URL routing, ViewSets, and Mixins."""

    def setUp(self):
        self.user1 = User.objects.create_user(username="creator", password="pw")
        self.user2 = User.objects.create_user(username="viewer", password="pw")
        self.tag = Tag.objects.create(name="TestTag")

        self.post1 = Post.objects.create(
            title="Test Post 1",
            content="Content",
            user=self.user1,
            status=Post.StatusChoices.PUBLISHED,
        )
        self.post1.tags.add(self.tag)

        self.posts_url = "/api/posts"
        self.users_url = "/api/users"
        self.tags_url = "/api/tags"
        self.comments_url = "/api/comments"

        self.client.force_authenticate(user=self.user1)

    def test_url_routing_posts(self):
        """Verify the 'post-list' URL resolves correctly."""
        resolved = resolve(self.posts_url)
        self.assertEqual(resolved.func.cls, PostViewSet)

    def test_url_routing_users(self):
        """Verify the 'user-list' URL resolves correctly."""
        resolved = resolve(self.users_url)
        self.assertEqual(resolved.func.cls, UserDetailSet)

    def test_mixin_view_set_add_user_on_create(self):
        """Verify ViewSetAddUser mixin sets the current user on creation."""
        response = self.client.post(
            self.posts_url,
            {
                "title": "New Post",
                "content": "Test mixin",
                "status": Post.StatusChoices.DRAFT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_post = Post.objects.get(pk=response.data["id"])
        self.assertEqual(new_post.user, self.user1)

    def test_mixin_add_include_query_param(self):
        """Verify AddIncludeQueryParam mixin handles dynamic fields exclusion."""

        # Fetch a post detail, requesting only 'user' (excluding 'comments' and 'tags')
        response = self.client.get(
            f"{self.posts_url}/{self.post1.id}", {"include": "user"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertNotIn("tags", response.data)
        self.assertNotIn("comments", response.data)

    def test_post_list_filter_by_status(self):
        """Verify PostViewSet filtering by status."""
        Post.objects.create(
            title="Draft", content="C", user=self.user1, status=Post.StatusChoices.DRAFT
        )

        response = self.client.get(
            self.posts_url, {"status": Post.StatusChoices.PUBLISHED}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Post 1")

    def test_user_detail_read_only(self):
        """Verify UserDetailSet is read-only (ReadOnlyModelViewSet)."""
        response_post = self.client.post(
            self.users_url,
            {"username": "newuser", "email": "a@a.com", "password": "p"},
            format="json",
        )
        self.assertEqual(response_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_get = self.client.get(f"{self.users_url}/{self.user1.id}")
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["username"], "creator")
