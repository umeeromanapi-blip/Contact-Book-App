from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class Contact(models.Model):
    """
    Contact entity representing a saved contact record.
    Epic 1-4 Complete:
    - user: Foreign key to Django User for multi-user isolation
    - name, phone, email, category, notes, is_favorite
    - created_at, updated_at
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contacts',
        null=True,
        blank=True,
        help_text="Owner user account for this contact"
    )
    name = models.CharField(
        max_length=100,
        help_text="Full name of the contact"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Phone number of the contact"
    )
    email = models.EmailField(
        max_length=100,
        blank=True,
        default='',
        help_text="Optional email address of the contact"
    )
    is_favorite = models.BooleanField(
        default=False,
        help_text="Mark contact as favorite/starred"
    )
    CATEGORY_CHOICES = [
        ('personal', 'Personal'),
        ('work', 'Work / Office'),
        ('family', 'Family'),
        ('friends', 'Friends'),
        ('vip', 'VIP / Client'),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='personal',
        blank=True,
        help_text="Category/group for the contact"
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes, address, or details"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id if self.user_id else None,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'category': self.category,
            'category_display': self.get_category_display(),
            'notes': self.notes,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    class Meta:
        db_table = 'contacts_contact'
        ordering = ['-id']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return f"{self.name} ({self.phone})"


class ActivityLog(models.Model):
    """
    Epic 4: Tracks audit trail of contact operations.
    """
    ACTION_CHOICES = [
        ('create', 'Created Contact'),
        ('update', 'Updated Contact'),
        ('delete', 'Deleted Contact'),
        ('favorite', 'Starred Contact'),
        ('import', 'Imported Contacts'),
        ('bulk', 'Bulk Action'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        null=True,
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contacts_activity_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action}: {self.description}"


def log_activity(user, action, description):
    """Helper to safely record an activity log entry."""
    try:
        ActivityLog.objects.create(
            user=user if (user and user.is_authenticated) else None,
            action=action,
            description=description
        )
    except Exception as e:
        logger.warning("Could not record activity log: %s", e)
