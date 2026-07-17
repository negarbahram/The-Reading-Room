from django.contrib import admin

from .models import Author, Book, BookCopy, Genre


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'publication_year', 'is_archived']
    list_filter = ['genre', 'is_archived', 'language']
    search_fields = ['title', 'author__name']
    inlines = [BookCopyInline]


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'book', 'status']
    list_filter = ['status']
