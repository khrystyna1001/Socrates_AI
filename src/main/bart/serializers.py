from rest_framework import serializers
from .models import BARTQuery


class BARTQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = BARTQuery
        fields = "__all__"
        read_only_fields = ("response", "created_at")
