from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("draft")
        PUBLISHED = "pblsh", _("published")

    title = models.CharField(max_length=250)
    content = models.TextField()
    status = models.CharField(
        max_length=5, choices=StatusChoices, default=StatusChoices.DRAFT
    )
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment {self.post} by {self.user}"
