from rest_framework import viewsets
from app.models import Fertilizer, CropNutrientRequirement, Crop
from app.serializers import FertilizerSerializer, CropNutrientRequirementSerializer, CropSerializer


class FertilizerViewSet (viewsets.ModelViewSet):
    queryset = Fertilizer.objects.all()
    serializer_class = FertilizerSerializer


class CropNutrientRequirementViewSet (viewsets.ModelViewSet):
    queryset = CropNutrientRequirement.objects.all()
    serializer_class = CropNutrientRequirementSerializer


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer