from rest_framework import viewsets
from app.models import Fertilizer, CropNutrientRequirement
from app.serializers import FertilizerSerializer, CropNutrientRequirementSerializer

class FertilizerViewSet (viewsets.ModelViewSet):
    queryset = Fertilizer.objects.all()
    serializer_class = FertilizerSerializer


class CropNutrientRequirementViewSet (viewsets.ModelViewSet):
    queryset = CropNutrientRequirement.objects.all()
    serializer_class = CropNutrientRequirementSerializer