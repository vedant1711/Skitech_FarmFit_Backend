from blogs.models import BlogEntry, CustomUser
from rest_framework import serializers


class BlogEntrySerializer (serializers.ModelSerializer):
    class Meta:
        model = BlogEntry
        fields = "__all__"


class CustomUserSerializer (serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
