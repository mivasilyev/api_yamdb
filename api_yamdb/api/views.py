from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from rest_framework import filters, generics, serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)


from api.serializers import (CategorySerializer, CommentSerializer,
                             ReviewSerializer, TitleSerializer, UserSerializer)
from api.permissions import IsAuthorOrReadOnlyPermission
from reviews.models import Category, Comment, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):  # удалить. Это пишет Марат.
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class CategoryViewSet(viewsets.ModelViewSet):  # удалить. Это пишет Марат.
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class TitleViewSet(viewsets.ModelViewSet):  # удалить. Это пишет Марат.
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)


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

#   /titles/{title_id}/reviews/:
#    GET: Получение списка всех отзывов, доступно без токена. 200/404
#    POST: Добавление нового отзыва, аутентифицированные. 201/400/401/404
#   /titles/{title_id}/reviews/{review_id}/:
#    GET: Получение отзыва по id, доступно без токена. 200/404
#    PATCH: Обновление отзыва по id, по токену. 200/400/401/403/404
#    DELETE: Удалить отзыв по id, по токену. 204/401/403/404


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review_id=self.get_review())

# /titles/{title_id}/reviews/{review_id}/comments/:
#  GET: Получение списка всех комментариев к отзыву, без токена. 200/404
#  POST: Добавление комментария к отзыву, по токену. 201/400/401/404
# /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/:
#  GET: Получение комментария к отзыву, без токена. 200/404
#  PATCH: Обновление комментария к отзыву, аутентифицированный. 200/400/401/403/404
#  DELETE: Удаление комментария к отзыву, автор, модератор, админ. 204/401/403/404
