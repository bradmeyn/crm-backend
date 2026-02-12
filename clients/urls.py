from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ClientViewSet, FileNoteViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')


urlpatterns = [
    path('', include(router.urls)),
    path('clients/<uuid:client_id>/file-notes/', FileNoteViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('clients/<uuid:client_id>/file-notes/<uuid:pk>/', FileNoteViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]