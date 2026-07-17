from datetime import timedelta

import pytest
from django.utils import timezone

from circulation.models import Loan
from reviews.models import Review

FUTURE_DUE = timezone.now() + timedelta(days=400)


@pytest.mark.django_db
class TestReviewEligibility:
    def test_cannot_review_without_borrowing(self, member_client, book):
        resp = member_client.post('/api/v1/reviews/', {'book': book.id, 'rating': 5, 'comment': 'Great'})
        assert resp.status_code == 400

    def test_can_review_after_borrowing(self, member_client, member, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        resp = member_client.post('/api/v1/reviews/', {'book': book_with_copy.id, 'rating': 5, 'comment': 'Great'})
        assert resp.status_code == 201

    def test_duplicate_review_rejected(self, member_client, member, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        member_client.post('/api/v1/reviews/', {'book': book_with_copy.id, 'rating': 5, 'comment': 'Great'})
        resp = member_client.post('/api/v1/reviews/', {'book': book_with_copy.id, 'rating': 3, 'comment': 'Again'})
        assert resp.status_code == 400

    def test_edit_own_review(self, member_client, member, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        resp = member_client.post('/api/v1/reviews/', {'book': book_with_copy.id, 'rating': 5, 'comment': 'Great'})
        review_id = resp.data['id']
        resp2 = member_client.patch(f'/api/v1/reviews/{review_id}/', {'rating': 4})
        assert resp2.status_code == 200
        assert resp2.data['rating'] == 4

    def test_cannot_edit_others_review(self, api_client, member, member2, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        review = Review.objects.create(member=member, book=book_with_copy, rating=5)
        api_client.force_authenticate(user=member2)
        resp = api_client.patch(f'/api/v1/reviews/{review.id}/', {'rating': 1})
        assert resp.status_code == 403


@pytest.mark.django_db
class TestReviewModeration:
    def test_unapproved_review_hidden_from_other_members(self, api_client, member, member2, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        Review.objects.create(member=member, book=book_with_copy, rating=1, is_approved=False)
        api_client.force_authenticate(user=member2)
        resp = api_client.get('/api/v1/reviews/', {'book': book_with_copy.id})
        assert len(resp.data['results']) == 0

    def test_admin_can_moderate_review(self, admin_client, member, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        review = Review.objects.create(member=member, book=book_with_copy, rating=1, is_approved=True)
        resp = admin_client.post(f'/api/v1/reviews/{review.id}/moderate/', {'is_approved': False})
        assert resp.status_code == 200
        review.refresh_from_db()
        assert review.is_approved is False


@pytest.mark.django_db
class TestAverageRating:
    def test_average_rating_calculated_from_approved_reviews(self, api_client, member, member2, book_with_copy):
        Loan.objects.create(member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
                             due_at=FUTURE_DUE)
        Review.objects.create(member=member, book=book_with_copy, rating=4, is_approved=True)
        Review.objects.create(member=member2, book=book_with_copy, rating=2, is_approved=False)
        resp = api_client.get(f'/api/v1/books/{book_with_copy.id}/')
        assert resp.data['average_rating'] == 4.0
