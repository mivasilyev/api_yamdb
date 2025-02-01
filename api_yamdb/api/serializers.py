import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.validators import UsernameRegexValidator, username_test
from api_yamdb.constants import (FORBIDDEN_NAME, MAX_LENTH,
                                 MAX_SCORE, MIN_SCORE)
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import current_year
from users.models import ROLES


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
        return username_test(value)


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

        if username == FORBIDDEN_NAME:
            raise ValidationError({
                'username': f'Имя пользователя {FORBIDDEN_NAME} не разрешено.'
            })

        if len(username) > MAX_LENTH:
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

    def create(self, validated_data):
        """Создание нового пользователя."""
        confirmation_code = random.randrange(1000, 9999)
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        if not created:
            confirmation_code = user.confirmation_code
        else:
            user.confirmation_code = confirmation_code
            user.role = ROLES[0][0]
            user.save()

        send_mail(
            'Код токена',
            f'Код для получения токена {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [validated_data['email']]
        )

        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена при регистрации."""

    username = serializers.CharField(
        required=True,
        validators=(UsernameRegexValidator(), )
    )
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        return username_test(value)


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


class TitleGetSerializer(serializers.ModelSerializer):
    """Для GET-запросов произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'category', 'genre', 'rating')


class TitleSerializer(serializers.ModelSerializer):
    """Для POST, PATCH и DELETE запросов произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        allow_empty=False
    )
    year = serializers.IntegerField(validators=(current_year,))

    def to_representation(self, instance):
        if self.context['request'].method == 'GET':
            serializer = TitleGetSerializer(instance)
            return serializer.data
        return super().to_representation(instance)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'category', 'genre',)


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        """Проверка на корректность оценки."""
        if (not (MIN_SCORE <= value <= MAX_SCORE)
                or not isinstance(value, int)):
            raise serializers.ValidationError(
                'Поставьте оценку целым числом от '
                f'{MIN_SCORE} до {MAX_SCORE}.'
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
        fields = ('id', 'text', 'author', 'pub_date')
