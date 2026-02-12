from django.contrib import admin
from django.utils.html import format_html
from .models import Client, FileNote, FileAttachment

class FileAttachmentInline(admin.TabularInline):
    model = FileAttachment
    extra = 1
    fields = ('file', 'name', 'file_size_display', 'uploaded_at', 'uploaded_by')
    readonly_fields = ('file_size_display', 'uploaded_at', 'uploaded_by')
    can_delete = True
    
    def file_size_display(self, obj):
        if obj.file_size:
            # Convert bytes to human readable format
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return '-'
    file_size_display.short_description = 'File Size'

class FileNoteInline(admin.TabularInline):
    model = FileNote
    extra = 0
    fields = ('title', 'note_type', 'attachment_count', 'created_at')
    readonly_fields = ('attachment_count', 'created_at')
    can_delete = True
    show_change_link = True
    
    def attachment_count(self, obj):
        if obj.pk:
            count = obj.attachments.count()
            return f"{count} file{'s' if count != 1 else ''}"
        return '-'
    attachment_count.short_description = 'Attachments'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'business_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'business', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [FileNoteInline]
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

@admin.register(FileNote)
class FileNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'note_type', 'attachment_count', 'is_private', 'created_at')
    list_filter = ('note_type', 'is_private', 'created_at', 'client')
    search_fields = ('title', 'body', 'client__first_name', 'client__last_name', 'client__email')
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [FileAttachmentInline]
    fieldsets = (
        (None, {
            'fields': ('id', 'client', 'title', 'body', 'note_type', 'is_private')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_name(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          f'/admin/clients/client/{obj.client.id}/change/',
                          obj.client.full_name())
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'client__last_name'
    
    def attachment_count(self, obj):
        count = obj.attachments.count()
        if count > 0:
            return format_html('<strong>{}</strong> file{}', count, 's' if count != 1 else '')
        return '-'
    attachment_count.short_description = 'Attachments'

@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_note_link', 'file_size_display', 'uploaded_at', 'uploaded_by')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('name', 'file_note__title', 'file_note__client__first_name', 'file_note__client__last_name')
    readonly_fields = ('id', 'uploaded_at', 'file_size_display')
    fieldsets = (
        (None, {
            'fields': ('id', 'file_note', 'file', 'name', 'file_size', 'file_size_display')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by', 'uploaded_at'),
        }),
    )
    
    def file_note_link(self, obj):
        return format_html('<a href="{}">{}</a>',
                          f'/admin/clients/filenote/{obj.file_note.id}/change/',
                          obj.file_note.title)
    file_note_link.short_description = 'File Note'
    file_note_link.admin_order_field = 'file_note__title'
    
    def file_size_display(self, obj):
        if obj.file_size:
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return '-'
    file_size_display.short_description = 'File Size'