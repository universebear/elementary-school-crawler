from rest_framework import serializers
from .models import FileBoard, Board


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'


class BoardFilesSerializer(serializers.ModelSerializer):
    file = serializers.FileField(read_only=True)

    class Meta:
        model = FileBoard
        fields = (
            'id',
            'subject',
            'file',
        )
