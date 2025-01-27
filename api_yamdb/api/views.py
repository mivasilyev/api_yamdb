import random
from pprint import pprint

import jwt
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, mixins, serializers, status,
                            viewsets, views, response)
# from rest_framework.authtoken.models import Token
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView

from api.filters import TitleManyFilters
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnlyPermission
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    TitleGetSerializer, TitleSerializer, UserSerializer,
    GetTokenSerializer, SingUpSerializer)
from reviews.models import Category, Comment, Genre, Review, Title, User
from users.models import ROLES


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для регистрации пользователей админом."""
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = (AllowAny,)  # (IsAdminUser,)


class UserSignUp(views.APIView):
    """Функция регистрации новых пользователей."""

    serializer_class = SingUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(
                username=serializer.validated_data.get('username'),
                email=serializer.validated_data.get('email')
            )
        except IntegrityError:
            return response.Response(
                settings.MESSAGE_EMAIL_EXISTS if
                User.objects.filter(username='username').exists()
                else settings.MESSAGE_USERNAME_EXISTS,
                status.HTTP_400_BAD_REQUEST
            )
        code = default_token_generator.make_token(user)
        send_mail(
            'Код токена',
            f'Код для получения токена {code}',
            settings.DEFAULT_FROM_EMAIL,
            [serializer.validated_data.get('email')]
        )
        return response.Response(
            serializer.data, status=status.HTTP_200_OK
        )


class UserGetToken(APIView):
    """Вью-класс получения токена по username и confirmation_code."""
    # queryset = User.objects.all()
    # serializer_class = UserSignupSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        
        """Функция получения токена при регистрации."""
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get(
            'confirmation_code'
        )
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token)}, status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST
        )


    # def post(self, request):
    #     serializer = CatSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).


class CategoryGenreViewset(
        viewsets.GenericViewSet, mixins.ListModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """Базовый сет для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreViewset):
    """Категории произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewset):
    """Жанры произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Произведения."""

    queryset = Title.objects.select_related(
        'category').prefetch_related('genre').all()
    serializer_class = TitleGetSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleManyFilters
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def update_rating(self):
        """Обновление рейтинга в модели Title."""
        title = self.get_title()
        avg_rating = title.reviews.aggregate(Avg('score', default=None))
        new_rating = avg_rating['score__avg']
        if new_rating is not None:
            new_rating = round(avg_rating['score__avg'])
        Title.objects.filter(id=title.id).update(rating=new_rating)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        if self.get_title().reviews.filter(author=self.request.user):
            raise serializers.ValidationError(
                'Вы не можете дважды дать отзыв на одно произведение.'
            )
        serializer.save(title_id=self.get_title(), author=self.request.user)
        # После записи отзыва обновляем рейтинг.
        self.update_rating()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.update_rating()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.update_rating()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review_id=self.get_review())

# /titles/{title_id}/reviews/:
#  GET: Получение списка всех отзывов, доступно без токена. 200/404
#  POST: Добавление нового отзыва, аутентифицированные. 201/400/401/404
# /titles/{title_id}/reviews/{review_id}/:
#  GET: Получение отзыва по id, доступно без токена. 200/404
#  PATCH: Обновление отзыва по id, по токену. 200/400/401/403/404
#  DELETE: Удалить отзыв по id, по токену. 204/401/403/404

# /titles/{title_id}/reviews/{review_id}/comments/:
#  GET: Получение списка всех комментариев к отзыву, без токена. 200/404
#  POST: Добавление комментария к отзыву, по токену. 201/400/401/404
# /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/:
#  GET: Получение комментария к отзыву, без токена. 200/404
#  PATCH: Обновление комментария к отзыву, аутентифицир. 200/400/401/403/404
#  DELETE: Удаление комментария к отзыву, автор, модер., админ. 204/401/403/404
