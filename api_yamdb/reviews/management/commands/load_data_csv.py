import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from api_yamdb.settings import BASE_DIR
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import ProjectUser

DATA_FILES_CSV = [
    'category.csv',
    'genre.csv',
    'titles.csv',
    'genre_title.csv',
    'users.csv',
    'comments.csv',
    'review.csv',
]


class Command(BaseCommand):
    """Скрипт для загрузки данных."""

    help = ('Импортирует данные из CSV-файлов в модели,'
            f'из каталога: {BASE_DIR}/static/data/')

    @transaction.atomic
    def handle(self, *args, **options):
        cnt = 0
        for file_name in DATA_FILES_CSV:
            file_path = f'{BASE_DIR}/static/data/{file_name}'
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=",")
                for row in reader:
                    if 'category.csv' == file_name:
                        Category.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            slug=row['slug']
                        )
                    elif 'genre.csv' == file_name:
                        Genre.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            slug=row['slug']
                        )
                    elif 'titles.csv' == file_name:
                        Title.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            year=row['year'],
                            category_id=row['category'],
                        )
                    elif 'genre_title.csv' == file_name:
                        GenreTitle.objects.update_or_create(
                            id=row['id'],
                            title_id=row['title_id'],
                            genre_id=row['genre_id']
                        )
                    elif 'users.csv' == file_name:
                        ProjectUser.objects.update_or_create(
                            id=row['id'],
                            username=row['username'],
                            email=row['email'],
                            role=row['role'],
                            bio=row['bio'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                        )
                    elif 'review.csv' == file_name:
                        Review.objects.update_or_create(
                            id=row['id'],
                            title_id=row['title_id'],
                            text=row['text'],
                            author_id=row['author'],
                            score=row['score'],
                            pub_date=row['pub_date']
                        )
                    elif 'comments.csv' == file_name:
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
