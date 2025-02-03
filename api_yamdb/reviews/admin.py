from django.contrib import admin
from django.db.models import Avg

from reviews.models import Category, Comment, Genre, Review, Title, GenreTitle


class GenreTitleInline(admin.StackedInline):
    model = GenreTitle
    extra = 1
    verbose_name = 'жанр'
    verbose_name_plural = 'Жанры'


class TitleInline(admin.TabularInline):
    model = Title
    extra = 0
    verbose_name = 'произведение'
    verbose_name_plural = 'Произведения'


class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий."""

    inlines = (TitleInline,)
    list_display = ('name', 'slug', 'view_titles')
    search_fields = ('name',)
    list_filter = ('slug',)

    @admin.display(description='Произведений')
    def view_titles(self, obj):
        return obj.titles.all().count()


class GenreAdmin(admin.ModelAdmin):
    """Админка для жанров."""

    list_display = ('name', 'slug', 'view_titles')
    search_fields = ('name',)
    list_filter = ('slug',)

    @admin.display(description='Произведений')
    def view_titles(self, obj):
        return obj.titles.all().count()


class TitleAdmin(admin.ModelAdmin):
    """Админка для произведений."""

    inlines = (GenreTitleInline,)
    list_display = ('name', 'category', 'view_genres', 'view_reviews',
                    'view_rating')
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('category', 'genre')
    list_display_links = ('name',)
    empty_value_display = 'Не задано'

    @admin.display(description='Жанры')
    def view_genres(self, obj):
        genres_qs = obj.title_genres.all()
        genres = [genre.genre.name for genre in genres_qs]
        return ', '.join(genres)

    @admin.display(description='Отзывов')
    def view_reviews(self, obj):
        return obj.reviews.all().count()

    @admin.display(description='Рейтинг')
    def view_rating(self, obj):
        rating = obj.reviews.aggregate(
            Avg('score', default=None))['score__avg']
        return round(rating) if rating is not None else rating


class ReviewAdmin(admin.ModelAdmin):
    """Админка для отзывов."""

    list_display = ('title', 'score', 'author', 'text', 'comments_count',
                    'pub_date')
    list_display_links = ('text',)
    search_fields = ('title', 'author', 'score')
    list_filter = ('title', 'author', 'score')

    @admin.display(description='Комментариев')
    def comments_count(self, obj):
        comments = obj.comments.all().count()
        return comments


class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев."""

    list_display = ('review_id', 'author', 'text', 'pub_date')
    list_display_links = ('text',)
    list_filter = ('author',)


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
