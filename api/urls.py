from django.urls import path, include
from rest_framework.routers import DefaultRouter


from api.views import (
    UserViewSet,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    TokenCreate,
    UserConfirm,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'categories', CategoryViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')

auth_urls = [
    path('email/', TokenCreate.as_view()),
    path('token/', UserConfirm.as_view(), name='get_jwt_token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/', include(router.urls)),
]
