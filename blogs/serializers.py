from blogs.models import BlogEntry
from rest_framework import serializers


class BlogEntrySerializer (serializers.ModelSerializer):
    class Meta:
        model = BlogEntry
        fields = "__all__"
