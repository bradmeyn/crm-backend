from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('clients/<int:client_id>/notes/', views.NoteViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('clients/<int:client_id>/notes/<int:pk>/', views.NoteViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]