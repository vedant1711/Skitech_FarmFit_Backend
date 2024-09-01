from rest_framework import serializers
from app.models import Fertilizer, CropNutrientRequirement, Crop


class FertilizerSerializer (serializers.ModelSerializer):
    class Meta:
        model = Fertilizer
        fields = "__all__"


class CropNutrientRequirementSerializer (serializers.ModelSerializer):
    class Meta:
        model = CropNutrientRequirement
        fields = "__all__"


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'


class WeatherDataSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    wind_speed = serializers.FloatField()
    humidity = serializers.FloatField()
    pressure = serializers.FloatField()

