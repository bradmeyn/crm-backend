from django.db import models
import uuid


class AuditModel(models.Model):
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='%(class)s_created',
        null=True
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    preferred_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    street_address = models.CharField(max_length=255, blank=True)
    suburb = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=3, blank=True)
    postcode = models.CharField(max_length=4, blank=True)
    country = models.CharField(max_length=100, default='Australia')
    
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
    is_active = models.BooleanField(default=True)
    
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
    
    tax_file_number = models.CharField(max_length=11, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    quick_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
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


class FileNote(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='file_notes'
    )
    
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    
    class FileNoteType(models.TextChoices):
        GENERAL = 'GENERAL', 'General Note'
        MEETING = 'MEETING', 'Meeting Notes'
        PHONE_CALL = 'PHONE_CALL', 'Phone Call'
        EMAIL = 'EMAIL', 'Email'
        DOCUMENT = 'DOCUMENT', 'Document'
        COMPLIANCE = 'COMPLIANCE', 'Compliance'
    
    note_type = models.CharField(
        max_length=20,
        choices=FileNoteType.choices,
        default=FileNoteType.GENERAL
    )
    is_private = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'File Note'
        verbose_name_plural = 'File Notes'

    def __str__(self):
        return f"{self.title} - {self.client.full_name()}"


class ClientDocument(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    # Optional - set when document is uploaded in context of a note
    file_note = models.ForeignKey(
        'FileNote',
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True
    )

    class DocumentCategory(models.TextChoices):
        IDENTIFICATION = 'IDENTIFICATION', 'Identification'
        FINANCIAL = 'FINANCIAL', 'Financial'
        COMPLIANCE = 'COMPLIANCE', 'Compliance'
        SOA = 'SOA', 'Statement of Advice'
        TAX = 'TAX', 'Tax'
        INSURANCE = 'INSURANCE', 'Insurance'
        OTHER = 'OTHER', 'Other'

    file = models.FileField(upload_to='client_documents/%Y/%m/')
    name = models.CharField(max_length=255)
    size = models.IntegerField()
    category = models.CharField(
        max_length=20,
        choices=DocumentCategory.choices,
        default=DocumentCategory.OTHER
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Client Document'
        verbose_name_plural = 'Client Documents'

    def __str__(self):
        return f"{self.name} - {self.client.full_name()}"