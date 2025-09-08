from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Client, Note
from .serializers import ClientSerializer, NoteSerializer


class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientSerializer
    
    def get_queryset(self):
        # Filter clients by user's business_id
        return Client.objects.filter(business_id=self.request.user.business_id)
    
    def perform_create(self, serializer):
        print("Performing create with user business:", self.request.user)
        # Automatically add business_id when creating
        serializer.save(business=self.request.user.business)

    # def create(self, request, *args, **kwargs):
    #     print("Request data:", request.data)  # Debug line
    #     serializer = self.get_serializer(data=request.data)
    #     if not serializer.is_valid():
    #         print("Validation errors:", serializer.errors)  # Debug line
    #     return super().create(request, *args, **kwargs)


# class NoteViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated] 
#     serializer_class = NoteSerializer
    
#     def get_queryset(self):
#         # Assuming notes are also business-scoped
#         return Note.objects.filter(business_id=self.request.user.business_id)
    
#     def perform_create(self, serializer):
#         # Add business_id for notes too
#         serializer.save(business_id=self.request.user.business_id)