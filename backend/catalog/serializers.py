from rest_framework import serializers

from .models import Author, Book, BookCopy, Genre


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = ['id', 'book', 'barcode', 'status', 'shelf_location', 'acquired_at', 'notes']
        read_only_fields = ['acquired_at']


class BookListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    available_copies = serializers.IntegerField(source='available_copies_count', read_only=True)
    total_copies = serializers.IntegerField(source='total_copies_count', read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_name', 'genre', 'genre_name',
            'publication_year', 'cover_url', 'language', 'is_archived',
            'available_copies', 'total_copies', 'average_rating',
        ]

    def get_average_rating(self, obj):
        return getattr(obj, 'avg_rating', None)


class BookDetailSerializer(BookListSerializer):
    copies = BookCopySerializer(many=True, read_only=True)

    class Meta(BookListSerializer.Meta):
        fields = BookListSerializer.Meta.fields + [
            'isbn', 'publisher', 'description', 'shelf_location', 'copies',
        ]


class BookWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'genre', 'publication_year', 'isbn',
            'publisher', 'description', 'language', 'cover_url',
            'shelf_location', 'is_archived',
        ]
