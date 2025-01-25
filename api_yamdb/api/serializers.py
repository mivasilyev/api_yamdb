from django.db.models import Avg
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):  # удалить после отладки.

    class Meta:
        model = User
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Жанры."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    """Для GET-запросов произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'category', 'genre')
        read_only_fields = ('rating',)


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы."""

    title_id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('title_id', 'text', 'author', 'score', 'pub_date')  # 'rating'

    # def validate_title_id(self, value):
    #     author = self.context['request'].user
    #     if author == self.context['request'].user:
    #     # if Review.objects.filter(user=author, title_id=value).exists():
    #         raise serializers.ValidationError(  # value)
    #             'Вы не можете дважды дать отзыв на одно произведение.'
    #         )
    #     return value
# Как я понял, сериализатор не проверяет автоматически переданные поля.

    def validate_score(self, value):
        """Проверка на корректность оценки."""
        if not (1 <= value <= 10) or not isinstance(value, int):
            raise serializers.ValidationError(
                'Поставьте оценку целым числом от 1 до 10.'
            )
        return value

#     def validate_following(self, value):
#         user = self.context['request'].user
#         if user == value:
#             raise serializers.ValidationError(
#                 'Вы не можете подписаться на самого себя!'
#             )
#         if Follow.objects.filter(user=user, following=value).exists():
#             raise serializers.ValidationError(
#                 'Вы уже подписаны на этого пользователя.'
#             )
#         return value

# class CommentSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username'
#     )

#     class Meta:
#         model = Comment
#         fields = ('id', 'author', 'text', 'created', 'post')
#         read_only_fields = ('post',)

    # def create(self, validated_data):

    #     Review.objects.create(**validated_data)
    #     title_id = self.context['request'].title_id
    #     updated_rating = Review.objects.filter(
    #         title_id=title_id
    #     ).aggregate(avg_rating=Avg('score'), default=None)
    #     Title.objects.update(rating=int(updated_rating))


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии к отзывам."""

    # review_id = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='text'
    # )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('author', 'review_id', 'text', 'pub_date')
        read_only_fields = ('review_id', )
