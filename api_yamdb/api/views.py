from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, response, status,
                            views, viewsets)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView

from api.filters import TitleManyFilters
from api.permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorAdminModer
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             ReviewSerializer, SingUpSerializer,
                             TitleGetSerializer, TitleSerializer,
                             UsersSerializer)
from reviews.models import Category, Genre, Review, Title, User


class UsersViewSet(viewsets.ModelViewSet):
    """Функция работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    search_fields = ('username',)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            data = request.data.copy()
            data['role'] = user.role
            serializer = UsersSerializer(
                user, data=data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )
        serializer = UsersSerializer(user)
        return response.Response(
            serializer.data, status=status.HTTP_200_OK
        )


class UserSignUp(views.APIView):
    """Функция регистрации новых пользователей."""

    serializer_class = SingUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class UserGetToken(APIView):
    """Вью-класс получения токена по username и confirmation_code."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Функция получения токена при регистрации."""

        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


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

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).select_related(
            'category').prefetch_related('genre').all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleManyFilters
    ordering_fields = ('name', 'year', 'category')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Обзоры на произведения."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorAdminModer, IsAuthenticatedOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(title=self.get_title(), author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к обзорам на произведения."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthorAdminModer, IsAuthenticatedOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review_id=self.get_review())
