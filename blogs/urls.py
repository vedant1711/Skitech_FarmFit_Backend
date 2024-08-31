from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blogs.views import BlogEntryViewSet

router = DefaultRouter()
router.register(r'', BlogEntryViewSet, basename='blogentry')

urlpatterns = [
    path('', include(router.urls)),
]
