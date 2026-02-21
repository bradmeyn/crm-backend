from django.contrib import admin
from django.utils.html import format_html
from .models import Client, ClientDocument, FileNote


def human_readable_size(size):
    if size is None:
        return '-'
    value = float(size)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


class FileNoteInline(admin.TabularInline):
    model = FileNote
    extra = 0
    fields = ('title', 'note_type', 'is_private', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


class ClientDocumentInline(admin.TabularInline):
    model = ClientDocument
    extra = 0
    fields = ('name', 'category', 'size_display', 'created_at')
    readonly_fields = ('size_display', 'created_at')
    show_change_link = True

    def size_display(self, obj):
        return human_readable_size(obj.size)
    size_display.short_description = 'File Size'


class AuditAdminMixin:
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Client)
class ClientAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'business_name', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'business', 'primary_advisor', 'created_at')
    search_fields = (
        'first_name',
        'last_name',
        'preferred_name',
        'email',
        'phone',
        'occupation',
        'employer',
    )
    readonly_fields = ('id', 'age', 'created_by', 'updated_by', 'created_at', 'updated_at')
    inlines = [FileNoteInline, ClientDocumentInline]
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'id',
                ('title', 'first_name', 'last_name', 'preferred_name'),
                'date_of_birth',
                'age',
            )
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Address', {
            'fields': ('street_address', ('suburb', 'state', 'postcode'), 'country')
        }),
        ('Business & Status', {
            'fields': ('business', 'primary_advisor', 'status', 'is_active')
        }),
        ('Additional Details', {
            'fields': ('tax_file_number', 'occupation', 'employer', 'quick_note')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def business_name(self, obj):
        if not obj.business:
            return '-'
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/accounts/business/{obj.business.id}/change/',
            obj.business.name,
        )
    business_name.short_description = 'Business'
    business_name.admin_order_field = 'business__name'


@admin.register(FileNote)
class FileNoteAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'client_name', 'note_type', 'is_private', 'document_count', 'created_at')
    list_filter = ('note_type', 'is_private', 'created_at', 'client__business')
    search_fields = ('title', 'body', 'client__first_name', 'client__last_name', 'client__email')
    readonly_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')
    fieldsets = (
        ('File Note', {
            'fields': ('id', 'client', 'title', 'body', 'note_type', 'is_private')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def client_name(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/clients/client/{obj.client.id}/change/',
            obj.client.full_name(),
        )
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'client__last_name'

    def document_count(self, obj):
        count = obj.documents.count()
        if count > 0:
            return format_html('<strong>{}</strong> file{}', count, 's' if count != 1 else '')
        return '-'
    document_count.short_description = 'Documents'


@admin.register(ClientDocument)
class ClientDocumentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'client_name', 'category', 'size_display', 'created_at')
    list_filter = ('category', 'created_at', 'client__business')
    search_fields = ('name', 'description', 'client__first_name', 'client__last_name', 'client__email')
    readonly_fields = ('id', 'size_display', 'created_by', 'updated_by', 'created_at', 'updated_at')
    fieldsets = (
        ('Document', {
            'fields': ('id', 'client', 'file_note', 'file', 'name', 'category', 'size', 'size_display', 'description')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def client_name(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/clients/client/{obj.client.id}/change/',
            obj.client.full_name(),
        )
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'client__last_name'

    def size_display(self, obj):
        return human_readable_size(obj.size)
    size_display.short_description = 'File Size'