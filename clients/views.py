from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Client, FileNote, ClientDocument
from .serializers import ClientSerializer, FileNoteSerializer, ClientDocumentSerializer


class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientSerializer

    def get_queryset(self):
        return Client.objects.filter(
            business_id=self.request.user.business_id
        ).prefetch_related('file_notes', 'documents')

    def perform_create(self, serializer):
        serializer.save(
            business=self.request.user.business,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class FileNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FileNoteSerializer

    def get_queryset(self):
        return FileNote.objects.filter(
            client_id=self.kwargs['client_pk'],
            client__business_id=self.request.user.business_id
        ).prefetch_related('documents')

    def perform_create(self, serializer):
        serializer.save(
            client_id=self.kwargs['client_pk'],
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ClientDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return ClientDocument.objects.filter(
            client_id=self.kwargs['client_pk'],
            client__business_id=self.request.user.business_id
        )

    def perform_create(self, serializer):
        serializer.save(
            client_id=self.kwargs['client_pk'],
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
