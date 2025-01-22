from api.serializers import CommentSerializer, ReviewSerializer
from django.shortcuts import get_object_or_404, render
from rest_framework import filters, generics, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly)
from reviews.models import Comment, Review, Title


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny,)  # (IsAuthorOrReadOnlyPermission,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title_id=self.get_title())

#   /titles/{title_id}/reviews/:
#    GET: Получение списка всех отзывов, доступно без токена. 200/404
#    POST: Добавление нового отзыва, аутентифицированные. 201/400/401/404
#   /titles/{title_id}/reviews/{review_id}/:
#    GET: Получение отзыва по id, доступно без токена. 200/404
#    PATCH: Обновление отзыва по id, по токену. 200/400/401/403/404
#    DELETE: Удалить отзыв по id, по токену. 204/401/403/404


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)  # (IsAuthorOrReadOnlyPermission,)

    # def get_post(self):
    #     return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    # def get_queryset(self):
    #     return self.get_post().comments.all()

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user, post=self.get_post())

#   /titles/{title_id}/reviews/{review_id}/comments/:
#    GET: Получение списка всех комментариев к отзыву, без токена. 200/404
#    POST: Добавление комментария к отзыву, по токену. 201/400/401/404
#   /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/:
#    GET: Получение комментария к отзыву, без токена. 200/404
#    PATCH: Обновление комментария к отзыву, аутентифицированный. 200/400/401/403/404
#    DELETE: Удаление комментария к отзыву, автор, модератор, админ. 204/401/403/404
