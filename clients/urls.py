from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import ClientViewSet, FileNoteViewSet, ClientDocumentViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

clients_router = routers.NestedDefaultRouter(router, r'clients', lookup='client')
clients_router.register(r'file-notes', FileNoteViewSet, basename='client-file-notes')
clients_router.register(r'documents', ClientDocumentViewSet, basename='client-documents')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(clients_router.urls)),
]