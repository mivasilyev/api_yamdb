import random
from pprint import pprint

import jwt
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, mixins, serializers, status,
                            viewsets)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from api.filters import TitleManyFilters
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnlyPermission
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    TitleGetSerializer, TitleSerializer, UserSerializer, UserSignupSerializer)
from reviews.models import Category, Comment, Genre, Review, Title, User
from users.models import ROLES


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для регистрации пользователей админом."""
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny,)  # (IsAdminUser,)


class AdminCreatesUser(generics.CreateAPIView):
    """Вью-класс для запросов админа на регистрацию новых пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (IsAdminUser,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = random.randrange(1000, 9999)
        self.perform_create(serializer, confirmation_code)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_200_OK,
                        headers=headers)
    
    def perform_create(self, serializer, confirmation_code):
        serializer.save(
            confirmation_code=confirmation_code, role=ROLES[0][0])


class UserSignup(AdminCreatesUser):
    """Вью-класс для запросов на регистрацию новых пользователей."""
    permission_classes = (AllowAny,)

# class UserSignup(generics.CreateAPIView):
#     """Вью-класс для запросов на регистрацию новых пользователей."""
#     queryset = User.objects.all()
#     serializer_class = UserSignupSerializer
#     permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # confirmation_code = random.randrange(1000, 9999)
        # self.perform_create(serializer, confirmation_code)
        # headers = self.get_success_headers(serializer.data)
        email = request.data['email']
        send_mail(
            subject='Подтверждение подписки на YaMDb',
            message='Для завершения регистрации пользователя на YaMDb и '
            f'получения токена ваш код {confirmation_code}. Отправьте его POST'
            '-запросом на /api/v1/auth/token/ с параметрами '
            'username и confirmation_code.',
            from_email='from@api_yamdb.ru',
            recipient_list=[email]
        )
        return Response(serializer.data,
                        status=status.HTTP_200_OK,
                        headers=headers)

    def perform_create(self, serializer, confirmation_code):
        serializer.save(
            confirmation_code=confirmation_code,
            role=ROLES[0][0])


class UserGetToken(APIView):
    """Вью-класс получения токена по username и confirmation_code."""
    # queryset = User.objects.all()
    # serializer_class = UserSignupSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        # Проверяем наличие в базе username и confirmation_code.
        serializer = UserSignupSerializer(data=request.data)
        username = request.data['username']
        confirmation_code = request.data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code == confirmation_code:
            # здесь делаем токен и отправляем его в ответе.
            jwt_token = user.token
            return Response({'Token': jwt_token})
        raise serializers.ValidationError(
            'Пользователя с такими данными в системе не зарегистрировано.'
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
