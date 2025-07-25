import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.validators import UsernameRegexValidator, username_test
from api_yamdb.constants import FORBIDDEN_NAME, MAX_LENTH, MAX_SCORE, MIN_SCORE
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import current_year


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
        validators=[UsernameRegexValidator()]
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

        if len(email) > MAX_LENTH:
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

        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        if created:
            user.confirmation_code = random.randrange(1000, 9999)
            user.save()

        send_mail(
            'Код токена',
            f'Код для получения токена {user.confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [validated_data['email']]
        )

        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена при регистрации."""

    username = serializers.CharField(
        required=True,
        validators=(UsernameRegexValidator(),)
    )
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        return username_test(value)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != int(data['confirmation_code']):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения!'}
            )
        return data


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
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'category', 'genre',)


class TitleSerializer(TitleGetSerializer):
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
        return TitleGetSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        """Проверка на корректность оценки."""
        if (not isinstance(value, int)
                or not (MIN_SCORE <= value <= MAX_SCORE)):
            raise serializers.ValidationError(
                'Поставьте оценку целым числом от '
                f'{MIN_SCORE} до {MAX_SCORE}.'
            )
        return value

    def validate(self, data):
        if (
            self.context['request'].method == 'POST'
            and Review.objects.filter(
                author=self.context.get('request').user,
                title=self.context['view'].kwargs['title_id']
            ).exists()
        ):
            raise serializers.ValidationError(
                'Вы не можете дважды дать отзыв на одно произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
