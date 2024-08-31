from django.contrib import admin
from blogs.models import BlogEntry


class BlogEntryAdmin (admin.ModelAdmin):
    list_display = [field.name for field in BlogEntry._meta.fields]


# Register your models here.
admin.site.register(BlogEntry, BlogEntryAdmin)