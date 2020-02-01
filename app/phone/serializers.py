from rest_framework import serializers
from .models import FileUpload


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ('numbers', 'timestamp')


class PhoneSerializer(serializers.Serializer):
    """ Serializes the formatted phone numbers """
    number = serializers.CharField(max_length=14)
