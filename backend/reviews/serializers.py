from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    member_email = serializers.CharField(source='member.email', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'member', 'member_email', 'book', 'rating', 'comment', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['member', 'is_approved', 'created_at', 'updated_at']
