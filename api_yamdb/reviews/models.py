from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import current_year

User = get_user_model()


class Genre(models.Model):
    """Жанры произведений."""

    name = models.CharField('Жанр', max_length=256, )
    slug = models.SlugField(max_length=50,
                            help_text=('Идентификатор страницы для URL; '
                                       'разрешены символы латиницы, цифры, '
                                       'дефис и подчёркивание.'), unique=True,
                            verbose_name='Идентификатор жанра')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категории произведений."""

    name = models.CharField('Название категории', max_length=256, )
    slug = models.SlugField(max_length=50,
                            help_text=('Идентификатор страницы для URL; '
                                       'разрешены символы латиницы, цифры, '
                                       'дефис и подчёркивание.'), unique=True,
                            verbose_name='Идентификатор категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения."""

    name = models.CharField('Наименование произведения', max_length=256)
    year = models.PositiveSmallIntegerField(
        'Дата выхода произведения',
        validators=(current_year,))
    description = models.TextField('Описание', null=True, blank=True,
                                   help_text='Опишите произведение')
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='Название категории',
    )
    genres = models.ManyToManyField(
        Genre, through='TitleGenres',
        verbose_name='Жанры')

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenres(models.Model):
    """Связь произведений и жанров."""

    title = models.ForeignKey(
        Title, null=True, blank=True, on_delete=models.SET_NULL)
    genre = models.ForeignKey(
        Genre, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Произведение - жанр'
        verbose_name_plural = 'Произведение - жанры'

    def __str__(self):
        return f'{self.title.name} - {self.genre.name}'


class Review(models.Model):
    """Модель отзыва к произведению."""

    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveIntegerField(
        # Может принять значения от одного до десяти.
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            # На произведение пользователь может оставить только один отзыв.
            models.UniqueConstraint(
                fields=['title_id', 'author'],
                name='one_review_per_author'
            )
        ]


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Обзор'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
