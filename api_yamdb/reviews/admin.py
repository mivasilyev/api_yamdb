from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title


class TitleAdmin(admin.ModelAdmin):
    """Админка для произведений."""

    list_display = ('name', 'category', 'view_genres')
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('category',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'
    filter_horizontal = ('genre',)

    @admin.display(description='Жанры')
    def view_genres(self, obj):
        genres_qs = obj.title_genres.all()
        genres = []
        for genre in genres_qs:
            genres.append(genre.genre.name)
        return ', '.join(genres)


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Comment)
