from django.db import models
import uuid

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal Info
    title = models.CharField(max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    preferred_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)  # ADD - important for financial planning
    
    # Contact Info
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address
    street_address = models.CharField(max_length=255, blank=True)
    suburb = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=3, blank=True)  # NSW, VIC, etc.
    postcode = models.CharField(max_length=4, blank=True)
    country = models.CharField(max_length=100, default='Australia')
    
    # Client Status 
    class ClientStatus(models.TextChoices):
        PROSPECT = 'PROSPECT', 'Prospect'
        ACTIVE = 'ACTIVE', 'Active Client'
        INACTIVE = 'INACTIVE', 'Inactive'
        ARCHIVED = 'ARCHIVED', 'Archived'
    
    status = models.CharField(
        max_length=20,
        choices=ClientStatus.choices,
        default=ClientStatus.PROSPECT
    )
    is_active = models.BooleanField(default=True)  # Keep this too
    
    # Relationships
    business = models.ForeignKey(
        'accounts.Business',
        on_delete=models.CASCADE,
        related_name='clients'
    )
    primary_advisor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='primary_clients',
        null=True,
        blank=True
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='clients_created',
        null=True
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='clients_updated',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional useful fields
    tax_file_number = models.CharField(max_length=11, blank=True)  # TFN - sensitive!
    occupation = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    
    # Custom notes field for quick reference
    quick_note = models.TextField(blank=True)  # Quick notes, not same as FileNote model

    class Meta:
        ordering = ['-created_at']
        indexes = [  # ADD - performance
            models.Index(fields=['email']),
            models.Index(fields=['business', 'status']),
            models.Index(fields=['primary_advisor']),
        ]

    def __str__(self):
        if self.preferred_name:
            return f"{self.preferred_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):  
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

class FileNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        'Client', 
        on_delete=models.CASCADE,
        related_name='file_notes'
    )
    
    # Content
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True) 
    
    # Categorization
    class NoteType(models.TextChoices):
        GENERAL = 'GENERAL', 'General Note'
        MEETING = 'MEETING', 'Meeting Notes'
        PHONE_CALL = 'PHONE_CALL', 'Phone Call'
        EMAIL = 'EMAIL', 'Email'
        DOCUMENT = 'DOCUMENT', 'Document'
        COMPLIANCE = 'COMPLIANCE', 'Compliance'
    
    note_type = models.CharField(
        max_length=20, 
        choices=NoteType.choices, 
        default=NoteType.GENERAL
    )
    

    
    # Audit fields - CRITICAL for compliance
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,  # Don't delete notes if user is deleted
        related_name='file_notes_created',
        null=True
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='file_notes_updated',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Visibility/privacy
    is_private = models.BooleanField(default=False)  # Only visible to creator?
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'File Note'
        verbose_name_plural = 'File Notes'

    def __str__(self):
        return f"{self.title} - {self.client.full_name()}"
    

class FileAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_note = models.ForeignKey(
        'FileNote',
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='file_notes/%Y/%m/')
    name = models.CharField(max_length=255)
    size = models.IntegerField()  # in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)