from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('books', views.BookViewSet, basename='book')
router.register('authors', views.AuthorViewSet, basename='author')
router.register('genres', views.GenreViewSet, basename='genre')
router.register('book-copies', views.BookCopyViewSet, basename='bookcopy')

urlpatterns = router.urls
