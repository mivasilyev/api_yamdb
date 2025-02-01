from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator)
from django.db import models

from api_yamdb.constants import MAX_SCORE, MIN_SCORE, LENG_MAX, LENG_CUT
from reviews.validators import current_year

User = get_user_model()


class BaseModelCategoryGenre(models.Model):
    """Абстрактная модель для категорий и жанров."""

    name = models.CharField('Наименование', max_length=LENG_MAX,)
    slug = models.SlugField(help_text=('Идентификатор страницы для URL; '
                                       'разрешены символы латиницы, цифры, '
                                       'дефис и подчёркивание.'),
                            unique=True,
                            verbose_name='Идентификатор жанра'
                            )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:LENG_CUT]


class Genre(BaseModelCategoryGenre):
    """Жанры произведений."""

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(BaseModelCategoryGenre):
    """Категории произведений."""

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Произведения."""

    name = models.CharField('Наименование произведения', max_length=256)
    year = models.SmallIntegerField(
        'Дата выхода произведения',
        validators=(current_year,)
    )
    rating = models.SmallIntegerField(
        default=None,
        blank=True,
        null=True,
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ]
    )
    description = models.TextField('Описание',
                                   null=True,
                                   blank=True,
                                   help_text='Опишите произведение'
                                   )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Название категории',
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанры'
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Связь произведений и жанров."""

    title = models.ForeignKey(
        Title, null=True, blank=True, on_delete=models.SET_NULL)
    genre = models.ForeignKey(
        Genre, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'произведение - жанр'
        verbose_name_plural = 'Произведения - жанры'

    def __str__(self):
        return f'{self.title.name} - {self.genre.name}'


class Review(models.Model):
    """Модель отзыва к произведению."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        help_text=(
            f'Оцените произведение в баллах от {MIN_SCORE} до {MAX_SCORE}, '
            f'где {MAX_SCORE} - наивысшая оценка.'),
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title_id', 'author'],
                name='one_review_per_author'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Комментарий')
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

    def __str__(self):
        return self.text
