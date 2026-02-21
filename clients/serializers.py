from rest_framework import serializers
from .models import Client, FileNote, ClientDocument


class ClientDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDocument
        fields = [
            'id', 'client', 'file_note', 'file', 'name', 'size',
            'category', 'description', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['name', 'size', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        file = validated_data['file']
        validated_data['name'] = file.name
        validated_data['size'] = file.size
        return super().create(validated_data)


class FileNoteSerializer(serializers.ModelSerializer):
    documents = ClientDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = FileNote
        fields = [
            'id', 'client', 'title', 'body', 'note_type',
            'is_private', 'documents', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ClientSerializer(serializers.ModelSerializer):
    file_notes = FileNoteSerializer(many=True, read_only=True)
    documents = ClientDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        exclude = ['business']
        read_only_fields = ['created_by', 'created_at', 'updated_at']