import django_filters

from .models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains')
    genre = django_filters.CharFilter(field_name='genre__name', lookup_expr='icontains')
    genre_id = django_filters.NumberFilter(field_name='genre_id')
    author_id = django_filters.NumberFilter(field_name='author_id')
    publication_year = django_filters.NumberFilter(field_name='publication_year')

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'publication_year']
