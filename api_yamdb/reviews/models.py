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
        verbose_name = 'жанр'
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
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения."""

    name = models.CharField('Наименование произведения', max_length=256)
    year = models.PositiveSmallIntegerField(
        'Дата выхода произведения',
        validators=(current_year,))
    rating = models.SmallIntegerField(
        default=None,
        blank=True,
        verbose_name='Рейтинг',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
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
        verbose_name = 'произведение'
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
        verbose_name = 'произведение - жанр'
        verbose_name_plural = 'Произведения - жанры'

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
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        help_text=('Оцените произведение в баллах от 1 до 10'
                   ', где 10 - наивысшая оценка.'),
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


# class Score(models.Model):
#     """Модель рейтинга произведения."""

#     title_id = models.OneToOneField(
#         Title,
#         on_delete=models.CASCADE
#     )
#     rating = models.SmallIntegerField(choices=DEFAULT_CHOICES)

#     class Meta:
#         constraints = [
#             # На произведение пользователь может оставить только один отзыв.
#             models.UniqueConstraint(
#                 fields=['title_id', 'author'],
#                 name='one_review_per_author'
#             )
#         ]

# class Post(models.Model):
#     school_name = models.CharField(max_length=200, default='')
#     country = models.CharField(max_length=200, default='KZ')
#     city = models.CharField(max_length=200, default='')
#     content = models.TextField()
#     website = models.CharField(max_length=200, default='')
#     your_email = models.EmailField(default='')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)

#     def rating(self):
#         comments = self.comments.all()
#         rating = 0
#         for i in comments:
#              rating = rating + i.score
#         return rating/len(comments)
