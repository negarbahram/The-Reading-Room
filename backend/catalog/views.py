from django.db.models import Avg, Count, Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrReadOnly

from .filters import BookFilter
from .models import Author, Book, BookCopy, Genre
from .serializers import (
    AuthorSerializer, BookCopySerializer, BookDetailSerializer,
    BookListSerializer, BookWriteSerializer, GenreSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']


def _annotate_ratings(qs):
    return qs.annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        rating_count=Count('reviews', filter=Q(reviews__is_approved=True)),
    )


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name', 'genre__name']
    ordering_fields = ['title', 'publication_year', 'created_at']

    def get_queryset(self):
        qs = Book.objects.select_related('author', 'genre').prefetch_related('copies')
        qs = _annotate_ratings(qs).order_by('title')
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return qs
        return qs.filter(is_archived=False)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BookWriteSerializer
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer

    def perform_destroy(self, instance):
        """Archiving only — books are never hard-deleted (preserves loan history)."""
        instance.is_archived = True
        instance.save(update_fields=['is_archived'])

    @action(detail=True, methods=['get', 'post'], url_path='copies',
            permission_classes=[IsAdminOrReadOnly])
    def copies(self, request, pk=None):
        book = self.get_object()
        if request.method == 'GET':
            return Response(BookCopySerializer(book.copies.all(), many=True).data)
        serializer = BookCopySerializer(data={**request.data, 'book': book.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['get'], url_path='related')
    def related(self, request, pk=None):
        from recommendations.services import related_books
        book = self.get_object()
        results = related_books(book)
        return Response(results)

    @action(detail=False, methods=['get'], url_path='recommendations',
            permission_classes=[permissions.IsAuthenticated])
    def recommendations(self, request):
        from recommendations.services import recommended_for_user
        results = recommended_for_user(request.user)
        return Response(results)


class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.select_related('book')
    serializer_class = BookCopySerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['status', 'book']
