from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import MemberInterest, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'is_suspended',
            'phone_number', 'date_joined',
        ]
        read_only_fields = ['id', 'role', 'is_suspended', 'date_joined']


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'is_suspended',
            'phone_number', 'date_joined', 'is_active',
        ]
        read_only_fields = ['id', 'email', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']

    def create(self, validated_data):
        return User.objects.create_user(role=User.Role.MEMBER, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account is inactive.')
        attrs['user'] = user
        return attrs


class MemberInterestSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source='genre.name', read_only=True, default=None)
    author_name = serializers.CharField(source='author.name', read_only=True, default=None)

    class Meta:
        model = MemberInterest
        fields = ['id', 'genre', 'author', 'genre_name', 'author_name']

    def validate(self, attrs):
        genre = attrs.get('genre')
        author = attrs.get('author')
        if not genre and not author:
            raise serializers.ValidationError('Provide a genre or an author.')
        if genre and author:
            raise serializers.ValidationError('Provide only one of genre or author.')
        return attrs
