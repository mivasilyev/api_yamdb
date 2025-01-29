from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import current_year
from api.validators import UsernameRegexValidator, username_me, len_email


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для новых юзеров."""

    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameRegexValidator()
        ]
    )

    class Meta:
        abstract = True
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')

    def validate_username(self, value):
        return username_me(value)

    def validate_email(self, value):
        return len_email(value)


class PersSerializer(UsersSerializer):
    """Сериализатор для пользователя."""

    class Meta(UsersSerializer.Meta):
        read_only_fields = ('role',)


class SingUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    email = serializers.EmailField(
        required=True,
    )
    username = serializers.CharField(
        required=True,
        validators=[UsernameRegexValidator(), ]
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        User = get_user_model()

        if username == 'me':
            raise ValidationError({
                'username': 'Имя пользователя "me" не разрешено.'
            })

        if len(username) > 150:
            raise ValidationError({
                'username': 'Имя пользователя слишком длинное.'
            })

        if len(email) > 150:
            raise ValidationError({
                'email': 'Емейл слишком длинный.'
            })

        both_exists = User.objects.filter(
            username=username,
            email=email
        ).exists()

        if both_exists:
            return data

        if User.objects.filter(username=username).exists():
            raise ValidationError({
                'username': 'Пользователь с таким именем уже существует.'
            })

        if User.objects.filter(email=email).exists():
            raise ValidationError({
                'email': 'Пользователь с таким email уже существует.'
            })

        return data


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена при регистрации."""

    username = serializers.CharField(
        required=True,
        validators=(UsernameRegexValidator(), )
    )
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        return username_me(value)


class CategorySerializer(serializers.ModelSerializer):
    """Категории."""

    slug = serializers.SlugField(
        max_length=50,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                message='Такой slug уже есть.'
            )
        ]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Жанры."""

    slug = serializers.SlugField(
        max_length=50,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Genre.objects.all(),
                message='Такой slug уже есть.'
            )
        ]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleGetSerializer(serializers.ModelSerializer):
    """Для GET-запросов произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'category', 'genre', 'rating')
        read_only_fields = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Для POST, PATCH и DELETE запросов произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    year = serializers.IntegerField(validators=(current_year,))

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'category', 'genre',)
        read_only_fields = ('id',)


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы."""

    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')  # 'rating'


    def validate_score(self, value):
        """Проверка на корректность оценки."""
        if not (1 <= value <= 10) or not isinstance(value, int):
            raise serializers.ValidationError(
                'Поставьте оценку целым числом от 1 до 10.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии к отзывам."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'review_id', 'text', 'pub_date')
        read_only_fields = ('review_id', )
