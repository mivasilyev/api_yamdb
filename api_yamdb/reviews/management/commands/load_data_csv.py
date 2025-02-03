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
                    if CATEGORY == file_name:
                        Category.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            slug=row['slug']
                        )
                    elif GENRE == file_name:
                        Genre.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            slug=row['slug']
                        )
                    elif TITLES == file_name:
                        Title.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            year=row['year'],
                            category_id=row['category'],
                        )
                    elif GENRE_TITLE == file_name:
                        GenreTitle.objects.update_or_create(
                            id=row['id'],
                            title_id=row['title_id'],
                            genre_id=row['genre_id']
                        )
                    elif USERS == file_name:
                        MyUser.objects.update_or_create(
                            id=row['id'],
                            username=row['username'],
                            email=row['email'],
                            role=row['role'],
                            bio=row['bio'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                        )
                    elif REVIEW == file_name:
                        Review.objects.update_or_create(
                            id=row['id'],
                            title_id=row['title_id'],
                            text=row['text'],
                            author_id=row['author'],
                            score=row['score'],
                            pub_date=row['pub_date']
                        )
                    elif COMMENTS == file_name:
                        Comment.objects.update_or_create(
                            id=row['id'],
                            review_id_id=row['review_id'],
                            text=row['text'],
                            author_id=row['author'],
                            pub_date=row['pub_date'],
                        )
                cnt += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Файл {file_name} загружен')
                )
        self.stdout.write(
            self.style.SUCCESS(f'Загрузка завершена. Файлов загружено: {cnt}'))
