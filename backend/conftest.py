import pytest
from rest_framework.test import APIClient

from accounts.models import User
from catalog.models import Author, Book, BookCopy, Genre
from circulation.models import LibraryPolicy


@pytest.fixture
def policy(db):
    return LibraryPolicy.current()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(email='admin@test.com', password='pass12345')


@pytest.fixture
def member(db):
    return User.objects.create_user(email='member@test.com', password='pass12345', first_name='Mem', last_name='Ber')


@pytest.fixture
def member2(db):
    return User.objects.create_user(email='member2@test.com', password='pass12345')


@pytest.fixture
def author(db):
    return Author.objects.create(name='Test Author')


@pytest.fixture
def genre(db):
    return Genre.objects.create(name='Test Genre')


@pytest.fixture
def book(db, author, genre):
    return Book.objects.create(title='Test Book', author=author, genre=genre, publication_year=2000)


@pytest.fixture
def book_with_copy(book):
    BookCopy.objects.create(book=book, barcode='BC-1')
    return book


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def member_client(api_client, member):
    api_client.force_authenticate(user=member)
    return api_client
