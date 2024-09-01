from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # Remove the username field
    email = None  # Remove the email field

    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_expert = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []  # No additional fields are required

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

class BlogEntry(models.Model):
    user = models.ForeignKey(CustomUser, related_name='blogs', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    title_image = models.CharField(max_length=500, blank=True, null=True)
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
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = (self.content_html[:157] + "...") if len(self.content_html) > 160 else self.content_html
        if not self.meta_keywords:
            self.meta_keywords = ",".join(slugify(self.title).split('-'))
        super(BlogEntry, self).save(*args, **kwargs)