from django.db import models


class Fertilizer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    nitrogen_content = models.FloatField(help_text="Percentage of nitrogen content")
    phosphorus_content = models.FloatField(help_text="Percentage of phosphorus content")
    potassium_content = models.FloatField(help_text="Percentage of potassium content")

    def __str__(self):
        return self.name


class CropNutrientRequirement(models.Model):
    crop_name = models.CharField(max_length=100, unique=True)
    nitrogen_needed = models.FloatField(help_text="Total nitrogen required in kg/ha")
    phosphorus_needed = models.FloatField(help_text="Total phosphorus required in kg/ha")
    potassium_needed = models.FloatField(help_text="Total potassium required in kg/ha")

    def __str__(self):
        return self.crop_name
