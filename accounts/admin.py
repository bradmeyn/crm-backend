from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, Business

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count(self, obj):
        return obj.business_users.count()
    user_count.short_description = 'Users'


class BusinessFilter(admin.SimpleListFilter):
    title = _('Business')
    parameter_name = 'business'
    
    def lookups(self, request, model_admin):
        businesses = Business.objects.all().order_by('name')
        return [(business.id, business.name) for business in businesses]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(business__id=self.value())
        return queryset


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_full_name',  'business_name', 'is_active', 'is_staff', 'last_login')
    list_filter = ('is_active', 'is_staff',  BusinessFilter, 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Business'), {'fields': ('business',)}),

        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'business'),
        }),
    )
    
    def business_name(self, obj):
        if obj.business:
            return format_html('<a href="{}">{}</a>',
                              f'/admin/accounts/business/{obj.business.id}/change/',
                              obj.business.name)
        return '-'
    business_name.short_description = 'Business'
    business_name.admin_order_field = 'business__name'
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'
    
    def save_model(self, request, obj, form, change):
        # If creating a new user without a password
        if not change and not obj.password:
            obj.set_password(form.cleaned_data.get('password1'))
        super().save_model(request, obj, form, change)