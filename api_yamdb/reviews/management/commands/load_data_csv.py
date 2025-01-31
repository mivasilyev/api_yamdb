import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from api_yamdb.settings import BASE_DIR
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import MyUser

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
        for file_name in DATA_FILES_CSV:
            file_path = f'{BASE_DIR}/static/data/{file_name}'
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(
                    file, 'r', delimiter=",")
                for row in reader:
                    if 'category.csv' in file:
                        Category.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            slug=row['slug']
                        )
                    if 'genre.csv' in file:
                        Genre.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            slug=row['slug']
                        )
                    if 'titles.csv' in file:
                        Title.objects.update_or_create(
                            id=row['id'],
                            name=row['name'],
                            year=row['year'],
                            category_id=row['category'],
                        )
                    if 'genre_title.csv' in file:
                        GenreTitle.objects.update_or_create(
                            id=row['id'],
                            title_id=row['title_id'],
                            genre_id=row['genre_id']
                        )
                    if 'users.csv' in file:
                        MyUser.objects.update_or_create(
                            id=row['id'],
                            username=row['username'],
                            email=row['email'],
                            role=row['role'],
                            bio=row['bio'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                        )
                    if 'review.csv' in file:
                        Review.objects.update_or_create(
                            id=row['id'],
                            title_id=row['title_id'],
                            text=row['text'],
                            author_id=row['author'],
                            score=row['score'],
                            pub_date=row['pub_date']
                        )
                    if 'comments.csv' in file:
                        Comment.objects.update_or_create(
                            id=row['id'],
                            review_id_id=row['review_id'],
                            text=row['text'],
                            author_id=row['author'],
                            pub_date=row['pub_date'],
                        )
                self.stdout.write(self.style.SUCCESS(
                    f'Файл: {file_name} загружен')
                )
