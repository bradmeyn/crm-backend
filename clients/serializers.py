from rest_framework import serializers
from .models import Client, FileNote, FileAttachment

class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = '__all__'


class FileNoteSerializer(serializers.ModelSerializer):
    attachments = FileAttachmentSerializer(many=True)
    class Meta:
        model = FileNote
        fields = ['id', 'title', 'body', 'created_at', 'updated_at', 'client', 'attachments']

class ClientSerializer(serializers.ModelSerializer):
    file_notes = FileNoteSerializer(many=True, read_only=True)  

    class Meta:
        model = Client
        exclude = ['business']  # Exclude business field to prevent client from setting it directly