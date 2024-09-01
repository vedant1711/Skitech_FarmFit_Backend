from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.crop_recommendation import CropRecommendationAPIView
from app.views.fertilizer_combination import FertilizerCombinationAPIView
from app.views.model_viewsets import FertilizerViewSet, CropNutrientRequirementViewSet, CropViewSet
from app.views.weather_insights import WeatherInsightsView

router = DefaultRouter()
router.register(r'fertilizers', FertilizerViewSet, basename='fertilizer')
router.register(r'crop-requirements', CropNutrientRequirementViewSet, basename='crop-requirement')
router.register('crop', CropViewSet, basename='crop')

urlpatterns = [
    path('', include(router.urls)),
    path('fertilizer-combinations/', FertilizerCombinationAPIView.as_view(), name='fertilizer-combinations'),
    path('crop-recommendation/', CropRecommendationAPIView.as_view(), name='crop-recommendation'),
    path('weather-insights', WeatherInsightsView.as_view(), name='weather-insights'),
]
