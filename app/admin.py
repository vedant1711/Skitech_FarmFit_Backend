from django.contrib import admin
from app.models import Fertilizer, CropNutrientRequirement


class FertilizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'nitrogen_content', 'phosphorus_content', 'potassium_content')
    search_fields = ('name',)
    list_filter = ('nitrogen_content', 'phosphorus_content', 'potassium_content')


class CropNutrientRequirementAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'nitrogen_needed', 'phosphorus_needed', 'potassium_needed')
    search_fields = ('crop_name',)
    list_filter = ('crop_name',)


# Register your models here.

admin.site.register(Fertilizer, FertilizerAdmin)
admin.site.register(CropNutrientRequirement, CropNutrientRequirementAdmin)
