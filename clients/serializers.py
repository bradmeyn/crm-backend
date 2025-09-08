from rest_framework import serializers
from .models import Client, Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'body', 'created_at', 'updated_at', 'client']

class ClientSerializer(serializers.ModelSerializer):
    # notes = NoteSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        exclude = ['business']  # Exclude business field to prevent client from setting it directly