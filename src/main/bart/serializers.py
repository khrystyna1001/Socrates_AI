from rest_framework import serializers
from .models import BARTQuery

class BARTQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = BARTQuery
        fields = '__all__'