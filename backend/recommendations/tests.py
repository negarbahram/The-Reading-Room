
import pytest

from accounts.models import MemberInterest
from catalog.models import Author, Book, Genre
from recommendations import services


@pytest.mark.django_db
class TestColdStartRecommendations:
    def test_new_member_gets_popularity_fallback(self, member, book_with_copy):
        results = services.recommended_for_user(member)
        assert isinstance(results, list)
        for item in results:
            assert item['reason']

    def test_popularity_fallback_excludes_archived(self, member, book):
        book.is_archived = True
        book.save()
        results = services.recommended_for_user(member)
        assert all(r['id'] != book.id for r in results)


@pytest.mark.django_db
class TestPersonalizedRecommendations:
    def test_recommends_same_genre_as_interest(self, db, member):
        author1 = Author.objects.create(name='Author One')
        author2 = Author.objects.create(name='Author Two')
        genre = Genre.objects.create(name='Sci-Fi')
        other_genre = Genre.objects.create(name='Romance')
        target = Book.objects.create(title='Space Odyssey', author=author1, genre=genre, publication_year=2000)
        Book.objects.create(title='Love Story', author=author2, genre=other_genre, publication_year=2000)

        MemberInterest.objects.create(user=member, genre=genre)

        results = services.recommended_for_user(member)
        result_ids = [r['id'] for r in results]
        assert target.id in result_ids
        target_entry = next(r for r in results if r['id'] == target.id)
        assert 'Sci-Fi' in target_entry['reason']

    def test_deterministic_reason_string_present(self, db, member):
        author = Author.objects.create(name='Determ Author')
        genre = Genre.objects.create(name='Determ Genre')
        book = Book.objects.create(title='Determ Book', author=author, genre=genre, publication_year=1999)
        MemberInterest.objects.create(user=member, author=author)
        results = services.recommended_for_user(member)
        assert any(r['id'] == book.id and r['reason'] for r in results)


@pytest.mark.django_db
class TestRelatedBooks:
    def test_related_books_prioritise_same_author(self, db, book, author):
        from catalog.models import Genre
        other_genre = Genre.objects.create(name='Other Genre')
        same_author_book = Book.objects.create(
            title='Sequel', author=author, genre=other_genre, publication_year=2001,
        )
        results = services.related_books(book)
        result_ids = [r['id'] for r in results]
        assert same_author_book.id in result_ids

    def test_related_books_excludes_self_and_archived(self, db, book, author, genre):
        archived = Book.objects.create(
            title='Archived Sibling', author=author, genre=genre, publication_year=2001, is_archived=True,
        )
        results = services.related_books(book)
        result_ids = [r['id'] for r in results]
        assert book.id not in result_ids
        assert archived.id not in result_ids
