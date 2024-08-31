from django.contrib import admin
from blogs.models import BlogEntry, CustomUser


class BlogEntryAdmin (admin.ModelAdmin):
    list_display = [field.name for field in BlogEntry._meta.fields]


class CustomUserAdmin (admin.ModelAdmin):
    list_display = [field.name for field in CustomUser._meta.fields]


# Register your models here.
admin.site.register(BlogEntry, BlogEntryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
