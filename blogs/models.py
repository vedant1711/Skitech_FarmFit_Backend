from django.db import models
from django.utils.text import slugify


class BlogEntry(models.Model):
    title = models.CharField(max_length=200)
    title_image = models.CharField(max_length=500, blank=True, null=True)  # URL for the title image
    content_html = models.TextField()
    content_json = models.JSONField(blank=True, null=True)
    content_markdown = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.CharField(max_length=160, blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Default metadata generation if not provided
        if not self.meta_title:
            self.meta_title = self.title[:60]  # Limiting to 60 characters
        if not self.meta_description:
            self.meta_description = (self.content_html[:157] + "...") if len(
                self.content_html) > 160 else self.content_html
        if not self.meta_keywords:
            self.meta_keywords = ",".join(slugify(self.title).split('-'))  # Basic keyword generation from the title

        super(BlogEntry, self).save(*args, **kwargs)