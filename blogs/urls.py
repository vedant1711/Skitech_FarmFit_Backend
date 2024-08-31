from django.urls import path, include
from blogs.views import BlogEntryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('blogs', BlogEntryViewSet, basename='blogs')

urlpatterns = [
    path('', include(router.urls)),
]
