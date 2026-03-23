from rest_framework import serializers
from .models import BARTModel

class BARTSerializer(serializers.ModelSerializer):
    class Meta:
        model = BARTModel
        fields = '__all__'