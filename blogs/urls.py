from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blogs.views import BlogEntryViewSet, CustomUserViewSet

router = DefaultRouter()
router.register(r'', BlogEntryViewSet, basename='blogentry')
router.register(r'', CustomUserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
]
