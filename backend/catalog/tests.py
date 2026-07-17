import pytest

from catalog.models import Author, Book, BookCopy, Genre


@pytest.mark.django_db
class TestCatalogPermissions:
    def test_anonymous_can_browse_books(self, api_client, book):
        resp = api_client.get('/api/v1/books/')
        assert resp.status_code == 200

    def test_member_cannot_create_book(self, member_client, author, genre):
        resp = member_client.post('/api/v1/books/', {
            'title': 'New Book', 'author': author.id, 'genre': genre.id, 'publication_year': 2020,
        })
        assert resp.status_code == 403

    def test_admin_can_create_book(self, admin_client, author, genre):
        resp = admin_client.post('/api/v1/books/', {
            'title': 'New Book', 'author': author.id, 'genre': genre.id, 'publication_year': 2020,
        })
        assert resp.status_code == 201

    def test_admin_archive_instead_of_delete(self, admin_client, book):
        resp = admin_client.delete(f'/api/v1/books/{book.id}/')
        assert resp.status_code == 204
        book.refresh_from_db()
        assert book.is_archived is True

    def test_archived_book_hidden_from_public_listing(self, api_client, book):
        book.is_archived = True
        book.save()
        resp = api_client.get('/api/v1/books/')
        titles = [b['title'] for b in resp.data['results']]
        assert book.title not in titles


@pytest.mark.django_db
class TestCatalogFiltering:
    @pytest.fixture(autouse=True)
    def _setup(self, db):
        a1 = Author.objects.create(name='Alpha Author')
        a2 = Author.objects.create(name='Beta Author')
        g1 = Genre.objects.create(name='Drama')
        g2 = Genre.objects.create(name='Comedy')
        self.b1 = Book.objects.create(title='Sunrise', author=a1, genre=g1, publication_year=2001)
        self.b2 = Book.objects.create(title='Sunset', author=a2, genre=g2, publication_year=2010)

    def test_filter_by_title(self, api_client):
        resp = api_client.get('/api/v1/books/', {'title': 'Sunrise'})
        titles = [b['title'] for b in resp.data['results']]
        assert titles == ['Sunrise']

    def test_filter_by_author(self, api_client):
        resp = api_client.get('/api/v1/books/', {'author': 'Alpha'})
        titles = [b['title'] for b in resp.data['results']]
        assert titles == ['Sunrise']

    def test_filter_by_genre(self, api_client):
        resp = api_client.get('/api/v1/books/', {'genre': 'Comedy'})
        titles = [b['title'] for b in resp.data['results']]
        assert titles == ['Sunset']

    def test_filter_by_publication_year(self, api_client):
        resp = api_client.get('/api/v1/books/', {'publication_year': 2010})
        titles = [b['title'] for b in resp.data['results']]
        assert titles == ['Sunset']


@pytest.mark.django_db
class TestAvailableCopiesCalculation:
    def test_available_copies_reflects_live_copy_states(self, book):
        BookCopy.objects.create(book=book, barcode='A1', status=BookCopy.Status.AVAILABLE)
        BookCopy.objects.create(book=book, barcode='A2', status=BookCopy.Status.ON_LOAN)
        BookCopy.objects.create(book=book, barcode='A3', status=BookCopy.Status.AVAILABLE)
        assert book.available_copies_count == 2
        assert book.total_copies_count == 3

    def test_archived_copies_excluded_from_total(self, book):
        BookCopy.objects.create(book=book, barcode='A1', status=BookCopy.Status.AVAILABLE)
        BookCopy.objects.create(book=book, barcode='A2', status=BookCopy.Status.ARCHIVED)
        assert book.total_copies_count == 1
