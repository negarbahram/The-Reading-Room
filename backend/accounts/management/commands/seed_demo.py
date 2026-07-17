"""Seed the database with demo accounts, catalog, loans, reviews, fines,
payments and recommendation-ready history. Idempotent-ish: safe to re-run
against a fresh database (uses get_or_create throughout).

Run with: python manage.py seed_demo
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import MemberInterest, User
from catalog.models import Author, Book, BookCopy, Genre
from circulation import services
from circulation.models import Fine, Loan, LoanRequest, LibraryPolicy
from notifications.models import NotificationPreference
from payments import services as payment_services
from reviews.models import Review


GENRES = ['Fiction', 'Science Fiction', 'Fantasy', 'Mystery', 'Romance',
          'History', 'Biography', 'Science', 'Poetry', 'Horror']

AUTHORS = [
    'Jane Austen', 'George Orwell', 'Ursula K. Le Guin', 'Isaac Asimov',
    'Agatha Christie', 'J.R.R. Tolkien', 'Toni Morrison', 'Mary Shelley',
    'Arthur Conan Doyle', 'Chimamanda Ngozi Adichie', 'Frank Herbert',
    'Virginia Woolf',
]

def _cover(cover_id: int) -> str:
    """Remote Open Library cover image — no image files are stored in this repo."""
    return f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'


BOOKS = [
    # title, author, genre, year, language, cover_id (Open Library cover_i,
    # resolved via openlibrary.org/search.json matched on exact title+author)
    ('Pride and Prejudice', 'Jane Austen', 'Romance', 1813, 'EN', 14348537),
    ('Sense and Sensibility', 'Jane Austen', 'Romance', 1811, 'EN', 9278292),
    ('Nineteen Eighty-Four', 'George Orwell', 'Science Fiction', 1949, 'EN', 9267242),
    ('Animal Farm', 'George Orwell', 'Fiction', 1945, 'EN', 11261770),
    ('The Left Hand of Darkness', 'Ursula K. Le Guin', 'Science Fiction', 1969, 'EN', 10618463),
    ('A Wizard of Earthsea', 'Ursula K. Le Guin', 'Fantasy', 1968, 'EN', 13617691),
    ('Foundation', 'Isaac Asimov', 'Science Fiction', 1951, 'EN', 14612610),
    ('I, Robot', 'Isaac Asimov', 'Science Fiction', 1950, 'EN', 12385229),
    ('Murder on the Orient Express', 'Agatha Christie', 'Mystery', 1934, 'EN', 11100465),
    ('And Then There Were None', 'Agatha Christie', 'Mystery', 1939, 'EN', 11172296),
    ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 1937, 'EN', 14627509),
    ('The Fellowship of the Ring', 'J.R.R. Tolkien', 'Fantasy', 1954, 'EN', 14627060),
    ('Beloved', 'Toni Morrison', 'Fiction', 1987, 'EN', 8261367),
    ('Song of Solomon', 'Toni Morrison', 'Fiction', 1977, 'EN', 9317262),
    ('Frankenstein', 'Mary Shelley', 'Horror', 1818, 'EN', 12356249),
    ('The Adventures of Sherlock Holmes', 'Arthur Conan Doyle', 'Mystery', 1892, 'EN', 6717853),
    ('The Hound of the Baskervilles', 'Arthur Conan Doyle', 'Mystery', 1902, 'EN', 8063264),
    ('Half of a Yellow Sun', 'Chimamanda Ngozi Adichie', 'History', 2006, 'EN', 8472660),
    ('Americanah', 'Chimamanda Ngozi Adichie', 'Fiction', 2013, 'EN', 8474037),
    ('Dune', 'Frank Herbert', 'Science Fiction', 1965, 'EN', 11481354),
    ('Mrs Dalloway', 'Virginia Woolf', 'Fiction', 1925, 'EN', 6397580),
    ('A Room of One\'s Own', 'Virginia Woolf', 'Biography', 1929, 'EN', 6559057),
]

MEMBER_SEED = [
    ('member1@library.com', 'Amara', 'Diallo'),
    ('member2@library.com', 'Liam', 'Chen'),
    ('member3@library.com', 'Sofia', 'Rossi'),
    ('member4@library.com', 'Noah', 'Kim'),
    ('member5@library.com', 'Elena', 'Petrova'),
    ('member6@library.com', 'Yusuf', 'Karimi'),
]

DESCRIPTION_BANK = [
    'A sweeping tale of love, loss, and the search for belonging.',
    'A gripping mystery that keeps readers guessing until the final page.',
    'An imaginative journey through a world unlike our own.',
    'A thought-provoking exploration of power, freedom, and identity.',
    'A classic story beloved across generations of readers.',
]


class Command(BaseCommand):
    help = 'Seed demo accounts, catalog, circulation history, reviews, fines and payments.'

    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write('Seeding library policy...')
        LibraryPolicy.objects.get_or_create(pk=1, defaults={
            'loan_duration_days': 14, 'max_concurrent_loans': 5, 'grace_period_days': 1,
            'daily_late_fee': Decimal('0.50'), 'reservation_hold_days': 3,
        })

        self.stdout.write('Seeding genres and authors...')
        genres = {name: Genre.objects.get_or_create(name=name)[0] for name in GENRES}
        authors = {name: Author.objects.get_or_create(name=name)[0] for name in AUTHORS}

        self.stdout.write('Seeding books and copies...')
        books = []
        for i, (title, author, genre, year, lang, cover_id) in enumerate(BOOKS):
            cover_url = _cover(cover_id)
            book, _ = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': authors[author], 'genre': genres[genre], 'publication_year': year,
                    'language': lang, 'isbn': f'978-0-00000-{i:03d}-0',
                    'publisher': 'Demo Press', 'description': random.choice(DESCRIPTION_BANK),
                    'cover_url': cover_url, 'shelf_location': f'{genre[:2].upper()}-{i + 1}',
                },
            )
            if book.cover_url != cover_url:
                # Backfill covers onto a database seeded before covers existed.
                book.cover_url = cover_url
                book.save(update_fields=['cover_url'])
            books.append(book)
            copy_count = 3 if i % 3 == 0 else 2
            for c in range(copy_count):
                BookCopy.objects.get_or_create(
                    book=book, barcode=f'{book.id:04d}-{c + 1}',
                    defaults={'status': BookCopy.Status.AVAILABLE, 'shelf_location': book.shelf_location},
                )

        self.stdout.write('Seeding demo accounts...')
        admin, created = User.objects.get_or_create(
            email='admin@library.com',
            defaults={'first_name': 'Head', 'last_name': 'Librarian', 'role': User.Role.ADMIN,
                      'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('AdminPass123')
            admin.save()

        members = []
        for email, first, last in MEMBER_SEED:
            member, created = User.objects.get_or_create(
                email=email, defaults={'first_name': first, 'last_name': last, 'role': User.Role.MEMBER},
            )
            if created:
                member.set_password('MemberPass123')
                member.save()
            NotificationPreference.objects.get_or_create(user=member)
            members.append(member)

        self.stdout.write('Seeding member interests...')
        MemberInterest.objects.get_or_create(user=members[0], genre=genres['Science Fiction'])
        MemberInterest.objects.get_or_create(user=members[0], author=authors['Isaac Asimov'])
        MemberInterest.objects.get_or_create(user=members[1], genre=genres['Fantasy'])
        MemberInterest.objects.get_or_create(user=members[2], genre=genres['Mystery'])

        self.stdout.write('Seeding loan requests, loans, reservations, fines, payments...')
        now = timezone.now()

        def make_returned_loan(member, book, days_ago_borrowed, days_loan, late_days=0):
            copy = book.copies.filter(status=BookCopy.Status.AVAILABLE).first()
            if not copy:
                return None
            copy.status = BookCopy.Status.ON_LOAN
            copy.save(update_fields=['status'])
            borrowed_at = now - timedelta(days=days_ago_borrowed)
            due_at = borrowed_at + timedelta(days=days_loan)
            returned_at = due_at + timedelta(days=late_days) if late_days else due_at - timedelta(days=1)
            loan = Loan.objects.create(
                member=member, book=book, copy=copy, status=Loan.Status.RETURNED,
                due_at=due_at, returned_at=returned_at,
            )
            Loan.objects.filter(pk=loan.pk).update(borrowed_at=borrowed_at)
            copy.status = BookCopy.Status.AVAILABLE
            copy.save(update_fields=['status'])
            if late_days > 0:
                fine_amount = Decimal(max(late_days - 1, 0)) * Decimal('0.50')
                if fine_amount > 0:
                    Fine.objects.get_or_create(
                        member=member, loan=loan,
                        defaults={'amount': fine_amount, 'status': Fine.Status.UNPAID},
                    )
            return loan

        def make_active_loan(member, book, days_ago_borrowed, days_loan):
            copy = book.copies.filter(status=BookCopy.Status.AVAILABLE).first()
            if not copy:
                return None
            copy.status = BookCopy.Status.ON_LOAN
            copy.save(update_fields=['status'])
            borrowed_at = now - timedelta(days=days_ago_borrowed)
            due_at = borrowed_at + timedelta(days=days_loan)
            status = Loan.Status.OVERDUE if due_at < now else Loan.Status.ACTIVE
            loan = Loan.objects.create(member=member, book=book, copy=copy, status=status, due_at=due_at)
            Loan.objects.filter(pk=loan.pk).update(borrowed_at=borrowed_at)
            return loan

        # Reading history for recommendation signals (members 0-2 favor sci-fi/fantasy/mystery)
        make_returned_loan(members[0], books[6], 40, 14)   # Foundation
        make_returned_loan(members[0], books[7], 25, 14)   # I, Robot
        make_returned_loan(members[1], books[10], 30, 14)  # The Hobbit
        make_returned_loan(members[2], books[8], 20, 14)   # Murder on the Orient Express

        # Active + overdue loans
        make_active_loan(members[0], books[19], 5, 14)     # Dune, active
        make_active_loan(members[3], books[2], 20, 14)     # 1984, overdue
        make_active_loan(members[4], books[12], 3, 14)     # Beloved, active

        # A returned-late loan generating an unpaid fine
        make_returned_loan(members[5], books[3], 25, 14, late_days=5)

        # A paid fine, to demonstrate the payment flow end-to-end
        paid_loan = make_returned_loan(members[3], books[4], 40, 14, late_days=8)
        if paid_loan:
            paid_fine = Fine.objects.filter(loan=paid_loan).first()
            if paid_fine:
                payment = payment_services.create_checkout_session(paid_fine, members[3])
                payment_services.confirm_payment(payment, succeeded=True)

        # Pending loan requests awaiting admin decision
        LoanRequest.objects.get_or_create(member=members[1], book=books[13], defaults={'status': 'PENDING'})
        LoanRequest.objects.get_or_create(member=members[2], book=books[15], defaults={'status': 'PENDING'})

        # A reservation queue: exhaust a title's copies, then reserve
        scarce_book = books[16]
        for copy in scarce_book.copies.all():
            if copy.status == BookCopy.Status.AVAILABLE:
                copy.status = BookCopy.Status.ON_LOAN
                copy.save(update_fields=['status'])
        borrower = members[4]
        Loan.objects.get_or_create(
            member=borrower, book=scarce_book, copy=scarce_book.copies.first(),
            defaults={'status': Loan.Status.ACTIVE, 'due_at': now + timedelta(days=10)},
        )
        try:
            services.create_reservation(members[5], scarce_book)
        except Exception:
            pass

        self.stdout.write('Seeding reviews...')
        review_data = [
            (members[0], books[6], 5, 'A landmark of science fiction. Loved the scope of it.'),
            (members[0], books[7], 4, 'Clever robot stories, still holds up today.'),
            (members[1], books[10], 5, 'A cozy, thrilling adventure. Perfect introduction to fantasy.'),
            (members[2], books[8], 4, 'Christie at her best — a genuinely surprising mystery.'),
            (members[3], books[3], 5, 'Chillingly relevant and beautifully written.'),
        ]
        for member, book, rating, comment in review_data:
            if Loan.objects.filter(member=member, book=book).exists():
                Review.objects.get_or_create(
                    member=member, book=book, defaults={'rating': rating, 'comment': comment},
                )

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {len(books)} books, {len(members)} members, 1 admin.\n'
            f'Admin login: admin@library.com / AdminPass123\n'
            f'Member login: member1@library.com / MemberPass123 (through member6@library.com)'
        ))
