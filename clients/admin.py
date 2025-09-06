from django.contrib import admin
from django.utils.html import format_html
from .models import Client, Note

class NoteInline(admin.TabularInline):
    model = Note
    extra = 0
    fields = ('title', 'body', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    can_delete = True
    show_change_link = True

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'business_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'business', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [NoteInline]
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', ('first_name', 'last_name'), 'email', 'phone')
        }),
        ('Business Information', {
            'fields': ('business', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def business_name(self, obj):
        return obj.business.name if obj.business else '-'
    business_name.short_description = 'Business'
    
    def full_name_display(self, obj):
        return obj.full_name()
    full_name_display.short_description = 'Name'

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'client')
    search_fields = ('title', 'body', 'client__first_name', 'client__last_name', 'client__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'client', 'title', 'body')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_name(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          f'/admin/your_app_name/client/{obj.client.id}/change/',
                          obj.client.full_name())
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'client__last_name'