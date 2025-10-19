from django_filters import rest_framework as filters
from .models import Post


class PostFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = Post
        fields = ["status"]
