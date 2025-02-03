from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserGetToken,
    UserSignUp,
    UsersViewSet
)

v1_router = DefaultRouter()

v1_router.register('users', UsersViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('categories', CategoryViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

auth_urls = [
    path('signup/', UserSignUp.as_view()),
    path('token/', UserGetToken.as_view()),
]

urlpatterns = [
    path("v1/auth/", include(auth_urls)),
    path('v1/', include(v1_router.urls)),
]
