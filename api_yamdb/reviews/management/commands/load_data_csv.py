import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import MyUser

from api_yamdb.constants import (
    DATA_FILES_CSV, STATIC_PATH, CATEGORY, GENRE,
    TITLES, GENRE_TITLE, USERS, COMMENTS, REVIEW)


class Command(BaseCommand):
    """Скрипт для загрузки данных."""

    help = ('Импортирует данные из CSV-файлов в модели,'
            f'из каталога: {settings.BASE_DIR}{STATIC_PATH}')

    @transaction.atomic
    def handle(self, *args, **options):
        cnt = 0
        for file_name in DATA_FILES_CSV:
            file_path = f'{settings.BASE_DIR}{STATIC_PATH}{file_name}'
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=",")
                for row in reader:
                    if file_name == CATEGORY:
                        Category.objects.update_or_create(**row)
                    elif file_name == GENRE:
                        Genre.objects.update_or_create(**row)
                    elif file_name == TITLES:
                        # Заменяем в словаре row ключ на соотв. модели.
                        row['category_id'] = row['category']
                        del row['category']
                        Title.objects.update_or_create(**row)
                    elif file_name == GENRE_TITLE:
                        GenreTitle.objects.update_or_create(**row)
                    elif file_name == USERS:
                        MyUser.objects.update_or_create(**row)
                    elif file_name == REVIEW:
                        row['author_id'] = row['author']
                        del row['author']
                        Review.objects.update_or_create(**row)
                    elif file_name == COMMENTS:
                        row['review_id_id'] = row['review_id']
                        row['author_id'] = row['author']
                        del row['author'], row['review_id']
                        Comment.objects.update_or_create(**row)
                cnt += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Файл {file_name} загружен')
                )
        self.stdout.write(
            self.style.SUCCESS(f'Загрузка завершена. Файлов загружено: {cnt}'))
