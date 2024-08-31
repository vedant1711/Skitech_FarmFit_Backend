from rest_framework import serializers
from app.models import Fertilizer, CropNutrientRequirement


class FertilizerSerializer (serializers.ModelSerializer):
    class Meta:
        model = Fertilizer
        fields = "__all__"


class CropNutrientRequirementSerializer (serializers.ModelSerializer):
    class Meta:
        model = CropNutrientRequirement
        fields = "__all__"
