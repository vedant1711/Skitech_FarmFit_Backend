# Create your views here.
from rest_framework.decorators import action
from rest_framework.response import Response
from blogs.models import BlogEntry, CustomUser
from blogs.serializers import BlogEntrySerializer, CustomUserSerializer
from rest_framework import viewsets, status
from django.utils.text import slugify
from rest_framework.exceptions import NotFound


class CustomUserViewSet (viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class BlogEntryViewSet(viewsets.ModelViewSet):
    queryset = BlogEntry.objects.all()
    serializer_class = BlogEntrySerializer

    def get_object(self):
        lookup_field = self.kwargs.get('pk')

        # Check if lookup_field is a slug (string) or an ID (int)
        if lookup_field.isdigit():
            return super().get_object()
        else:
            try:
                blog_entry = BlogEntry.objects.get(slug=lookup_field)
                blog_entry.views += 1  # Increment the views
                blog_entry.save()  # Save the updated blog entry
                return blog_entry
            except BlogEntry.DoesNotExist:
                raise NotFound("Blog entry not found")

    def create(self, request, *args, **kwargs):
        # Generate or validate metadata if provided
        if 'meta_title' not in request.data:
            request.data['meta_title'] = request.data['title'][:60]
        if 'meta_description' not in request.data:
            request.data['meta_description'] = request.data['content_html'][:160]
        if 'meta_keywords' not in request.data:
            request.data['meta_keywords'] = ",".join(slugify(request.data['title']).split('-'))

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Update slug if title is changed
        if 'title' in request.data and request.data['title'] != instance.title:
            request.data['slug'] = slugify(request.data['title'])

        # Handle metadata updates
        if 'meta_title' not in request.data or not request.data['meta_title']:
            request.data['meta_title'] = request.data.get('title', instance.title)[:60]
        if 'meta_description' not in request.data or not request.data['meta_description']:
            request.data['meta_description'] = request.data.get('content_html', instance.content_html)[:160]
        if 'meta_keywords' not in request.data or not request.data['meta_keywords']:
            request.data['meta_keywords'] = ",".join(slugify(request.data.get('title', instance.title)).split('-'))

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def retrieve_metadata(self, request, pk=None):
        """Retrieve the metadata for a specific blog entry"""
        blog_entry = self.get_object()
        data = {
            'meta_title': blog_entry.meta_title,
            'meta_description': blog_entry.meta_description,
            'meta_keywords': blog_entry.meta_keywords
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_blogs(self, request, user_id=None):
        """
        Retrieve all blog posts of a specific user.
        """
        user = CustomUser.objects.get(id=user_id)
        blogs = BlogEntry.objects.filter(user=user)
        serializer = self.get_serializer(blogs, many=True)
        return Response(serializer.data)