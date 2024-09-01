from blogs.models import BlogEntry, CustomUser
from rest_framework import serializers
from django.contrib.auth import authenticate

class BlogEntrySerializer (serializers.ModelSerializer):
    class Meta:
        model = BlogEntry
        fields = "__all__"


class CustomUserSerializer (serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class SignupSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    is_expert = serializers.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'description', 'photo', 'is_expert', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            description=validated_data.get('description', ''),
            photo=validated_data.get('photo'),
            is_expert=validated_data.get('is_expert', False),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SigninSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        # Return the user object on successful authentication
        return user

