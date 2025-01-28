from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AdminCreatesUser,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserGetToken,
    UserSignup,
    UserViewSet
)

v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet)
v1_router.register(r'genres', GenreViewSet)
v1_router.register(r'categories', CategoryViewSet)
v1_router.register(r'titles', TitleViewSet)
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

urlpatterns = [
    path('v1/auth/signup/', UserSignup.as_view()),
    path('v1/auth/token/', UserGetToken.as_view()),
    path('v1/users/', AdminCreatesUser.as_view()),
    path('v1/', include(v1_router.urls)),
    path('v1/', include('djoser.urls')),  # Для управления пользователями
    path('v1/', include('djoser.urls.jwt')),  # Для управления JWT-токенами
]
# /api/v1/users/me/ После регистрации и получения токена пользователь
# может отправить PATCH-запрос на эндпоинт и заполнить поля в своём профайле
# (описание полей — в документации).

# api/v1/users/ Пользователей создаёт администратор — через админ-зону сайта
# или через POST-запрос на специальный эндпоинт api/v1/users/ (описание полей
# запроса для этого случая есть в документации). При создании пользователя не
# предполагается автоматическая отправка письма пользователю с кодом
# подтверждения. 
# После этого пользователь должен самостоятельно отправить свой email и
# username на эндпоинт /api/v1/auth/signup/ , в ответ ему должно прийти письмо
# с кодом подтверждения.

# Далее пользователь отправляет POST-запрос с параметрами username и
# confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему
# приходит token (JWT-токен), как и при самостоятельной регистрации.
