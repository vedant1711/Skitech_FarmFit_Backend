from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blogs.views import BlogEntryViewSet, CustomUserViewSet, SigninView, SignupView

router = DefaultRouter()
router.register(r'blogentry', BlogEntryViewSet, basename='blogentry')
router.register(r'users', CustomUserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
]
