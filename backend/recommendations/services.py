"""Content-based recommendation service.

Deliberately simple/rule-based (academic project, not production ML):
score candidate books by shared genre, shared author, shared language and
description-keyword overlap with a member's borrowing/rating/interest
signals, then fall back to popularity for cold-start users. Kept as a
single swappable module — `related_books` and `recommended_for_user` are
the two entry points other apps call.
"""
import re
from collections import Counter

from django.db.models import Count, Q

from catalog.models import Book
from catalog.serializers import BookListSerializer

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'to', 'is', 'it', 'for',
    'with', 'this', 'that', 'as', 'by', 'from', 'at', 'be', 'are', 'was',
    'his', 'her', 'their', 'its', 'about', 'into', 'story', 'novel', 'book',
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']+", (text or '').lower())
    return {w for w in words if len(w) > 3 and w not in STOPWORDS}


def _serialize(book, reason: str):
    data = BookListSerializer(book).data
    data['reason'] = reason
    return data


def related_books(book, limit=6):
    """Books similar to a single given book (used on the book-detail page)."""
    book_keywords = _keywords(book.description)
    candidates = (
        Book.objects.filter(is_archived=False)
        .exclude(pk=book.pk)
        .select_related('author', 'genre')
    )

    scored = []
    for candidate in candidates:
        score = 0
        reasons = []
        if candidate.genre_id == book.genre_id:
            score += 3
            reasons.append(f'the same genre ({book.genre.name})')
        if candidate.author_id == book.author_id:
            score += 4
            reasons.append(f'the same author ({book.author.name})')
        if candidate.language == book.language:
            score += 1
        shared_keywords = book_keywords & _keywords(candidate.description)
        if shared_keywords:
            score += min(len(shared_keywords), 3)
            reasons.append('similar themes')
        if score > 0:
            reason = 'Because it shares ' + ' and '.join(reasons) if reasons else 'Readers with similar taste liked this'
            scored.append((score, candidate, reason))

    scored.sort(key=lambda t: t[0], reverse=True)
    if not scored:
        return _popularity_fallback(limit, exclude_ids={book.pk})
    return [_serialize(c, reason) for _, c, reason in scored[:limit]]


def _member_signals(user):
    """Collect genre/author weights from interests, borrowing history and ratings."""
    from accounts.models import MemberInterest
    from circulation.models import Loan
    from reviews.models import Review

    genre_weights: Counter = Counter()
    author_weights: Counter = Counter()
    borrowed_book_ids = set()

    for interest in MemberInterest.objects.filter(user=user).select_related('genre', 'author'):
        if interest.genre_id:
            genre_weights[interest.genre_id] += 3
        if interest.author_id:
            author_weights[interest.author_id] += 3

    for loan in Loan.objects.filter(member=user).select_related('book'):
        genre_weights[loan.book.genre_id] += 2
        author_weights[loan.book.author_id] += 2
        borrowed_book_ids.add(loan.book_id)

    for review in Review.objects.filter(member=user, rating__gte=4).select_related('book'):
        genre_weights[review.book.genre_id] += 2
        author_weights[review.book.author_id] += 2

    return genre_weights, author_weights, borrowed_book_ids


def _popularity_fallback(limit, exclude_ids=None):
    exclude_ids = exclude_ids or set()
    qs = (
        Book.objects.filter(is_archived=False)
        .exclude(pk__in=exclude_ids)
        .annotate(loan_count=Count('loans'))
        .select_related('author', 'genre')
        .order_by('-loan_count', 'title')[:limit]
    )
    return [_serialize(b, 'Popular with other members') for b in qs]


def recommended_for_user(user, limit=8):
    genre_weights, author_weights, borrowed_book_ids = _member_signals(user)

    if not genre_weights and not author_weights:
        return _popularity_fallback(limit)

    top_genre_ids = {g for g, _ in genre_weights.most_common(3)}
    top_author_ids = {a for a, _ in author_weights.most_common(3)}

    genre_names = {}
    if top_genre_ids:
        from catalog.models import Genre
        genre_names = dict(Genre.objects.filter(id__in=top_genre_ids).values_list('id', 'name'))
    author_names = {}
    if top_author_ids:
        from catalog.models import Author
        author_names = dict(Author.objects.filter(id__in=top_author_ids).values_list('id', 'name'))

    candidates = (
        Book.objects.filter(is_archived=False)
        .filter(Q(genre_id__in=genre_weights.keys()) | Q(author_id__in=author_weights.keys()))
        .select_related('author', 'genre')
    )

    scored = []
    for candidate in candidates:
        score = genre_weights.get(candidate.genre_id, 0) + author_weights.get(candidate.author_id, 0)
        if candidate.id in borrowed_book_ids:
            score -= 5  # de-prioritise, don't fully exclude, "better alternatives" still win
        if score <= 0:
            continue
        if candidate.genre_id in top_genre_ids:
            reason = f'Because you enjoyed {genre_names.get(candidate.genre_id, "this genre")}'
        elif candidate.author_id in top_author_ids:
            reason = f'Because you read books by {author_names.get(candidate.author_id, "this author")}'
        else:
            reason = 'Based on your reading history'
        scored.append((score, candidate, reason))

    scored.sort(key=lambda t: t[0], reverse=True)
    results = [_serialize(c, reason) for _, c, reason in scored[:limit]]

    if len(results) < limit:
        seen_ids = {c.pk for _, c, _ in scored} | borrowed_book_ids
        results += _popularity_fallback(limit - len(results), exclude_ids=seen_ids)

    return results
