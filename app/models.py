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


class Crop(models.Model):
    name = models.CharField(max_length=255, unique=True)
    crop_type = models.CharField(max_length=255, blank=True, null=True)
    varieties = models.JSONField(blank=True, null=True)
    techniques_used = models.JSONField(blank=True, null=True)
    temperature = models.CharField(max_length=50, blank=True, null=True)
    rainfall = models.CharField(max_length=50, blank=True, null=True)
    soil_type = models.JSONField(blank=True, null=True)
    major_producers = models.JSONField(blank=True, null=True)
    highest_producer = models.CharField(max_length=255, blank=True, null=True)
    highest_per_hectare_yield = models.CharField(max_length=255, blank=True, null=True)
    research_centre = models.JSONField(blank=True, null=True)
    highest_producing_country = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
