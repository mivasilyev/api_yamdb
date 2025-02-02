from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title

admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
# Для произведений желательна возможность редактировать категории прямо в
# листе произведений. Кроме того нужно вывести список жанров через
# запятую в листе произведений (для этого придется написать метод).