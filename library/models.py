import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """A book category / genre, e.g. Fiction, Science, History."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extra information attached to Django's built-in User model.
    A UserProfile with is_librarian=True has access to the librarian/admin
    side of the site (managing books, issuing/returning books, etc).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    is_librarian = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({'Librarian' if self.is_librarian else 'Member'})"

    @property
    def is_staff_member(self):
        """True if this account should see the librarian dashboard."""
        return self.is_librarian or self.user.is_staff or self.user.is_superuser


def book_image_upload_path(instance, filename):
    return f'book_images/{instance.isbn}_{filename}'


class Book(models.Model):
    """A single title held by the library, with a number of copies."""

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(
        max_length=20,
        unique=True,
        help_text='13-digit ISBN number, e.g. 9780143039433',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
    )
    publisher = models.CharField(max_length=255, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    available_copies = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=book_image_upload_path, blank=True, null=True
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[self.pk])

    @property
    def is_available(self):
        return self.available_copies > 0

    def clean(self):
        if self.available_copies is not None and self.total_copies is not None:
            if self.available_copies > self.total_copies:
                raise ValidationError(
                    'Available copies cannot be greater than total copies.'
                )


class Issue(models.Model):
    """A record of a book being borrowed by a user."""

    STATUS_ISSUED = 'issued'
    STATUS_RETURNED = 'returned'
    STATUS_OVERDUE = 'overdue'

    STATUS_CHOICES = [
        (STATUS_ISSUED, 'Issued'),
        (STATUS_RETURNED, 'Returned'),
        (STATUS_OVERDUE, 'Overdue'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issues',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='issues',
    )
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_ISSUED
    )
    fine_amount = models.PositiveIntegerField(default=0)
    fine_paid = models.BooleanField(default=False)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books_issued_by_me',
        help_text='Librarian who processed this issue, if issued manually.',
    )

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.book.title} -> {self.user.username} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.due_date:
            from django.conf import settings as django_settings
            days = getattr(django_settings, 'BOOK_ISSUE_DAYS', 14)
            self.due_date = self.issue_date + datetime.timedelta(days=days)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == self.STATUS_RETURNED:
            return False
        return timezone.localdate() > self.due_date

    @property
    def late_days(self):
        """Number of days late, based on return date (or today if still out)."""
        end_date = self.return_date if self.return_date else timezone.localdate()
        delta = (end_date - self.due_date).days
        return max(delta, 0)

    @property
    def calculated_fine(self):
        from django.conf import settings as django_settings
        fine_per_day = getattr(django_settings, 'FINE_PER_DAY', 5)
        return self.late_days * fine_per_day

    def mark_returned(self):
        """Mark this issue as returned today, calculate fine, restock the book."""
        self.return_date = timezone.localdate()
        self.fine_amount = self.calculated_fine
        self.status = self.STATUS_RETURNED
        self.save()
        self.book.available_copies += 1
        self.book.save()
