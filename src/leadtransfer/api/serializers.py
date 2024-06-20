from rest_framework import serializers

from ..models import CRMContact


class CRMContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMContact
        fields = '__all__'
