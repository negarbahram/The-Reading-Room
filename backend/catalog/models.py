from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Bibliographic record. Physical inventory lives on BookCopy."""

    class Language(models.TextChoices):
        EN = 'EN', 'English'
        FR = 'FR', 'French'
        ES = 'ES', 'Spanish'
        AR = 'AR', 'Arabic'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=300)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='books')
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name='books')
    publication_year = models.PositiveIntegerField()
    isbn = models.CharField(max_length=20, blank=True, unique=True, null=True)
    publisher = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=10, choices=Language.choices, default=Language.EN)
    cover_url = models.URLField(blank=True)
    shelf_location = models.CharField(max_length=50, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['is_archived']),
        ]

    def __str__(self):
        return f'{self.title} ({self.publication_year})'

    @property
    def available_copies_count(self):
        return self.copies.filter(status=BookCopy.Status.AVAILABLE).count()

    @property
    def total_copies_count(self):
        return self.copies.exclude(status=BookCopy.Status.ARCHIVED).count()


class BookCopy(models.Model):
    """A single physical/circulating copy of a Book. Inventory = live copy states."""

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        ON_LOAN = 'ON_LOAN', 'On loan'
        HELD = 'HELD', 'Held for reservation'
        LOST = 'LOST', 'Lost'
        DAMAGED = 'DAMAGED', 'Damaged'
        ARCHIVED = 'ARCHIVED', 'Archived'

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    barcode = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE)
    shelf_location = models.CharField(max_length=50, blank=True)
    acquired_at = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['book', 'barcode']
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'{self.book.title} — copy {self.barcode} ({self.status})'
