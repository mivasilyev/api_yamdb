EMAIL_MAX_LENGTH = 254
MAX_LENTH = 150
FORBIDDEN_NAME = 'me'
VALID_USERNAME_PATTERN = r'^[\w.@+-]+\Z'

LENG_SLUG = 50
LENG_MAX = 256
LENG_DATA_USER = 150
LENG_EMAIL = 254
LENG_CUT = 30
LENG_APPENDIX = '...'

MESSAGE_EMAIL_EXISTS = 'Этот email уже занят'
MESSAGE_USERNAME_EXISTS = 'Это имя уже занято'

# Ограничения на оценку произведения.
MIN_SCORE = 1
MAX_SCORE = 10

# Константы для работы с файлами csv.
CATEGORY = 'category.csv'
GENRE = 'genre.csv'
TITLES = 'titles.csv'
GENRE_TITLE = 'genre_title.csv'
USERS = 'users.csv'
COMMENTS = 'comments.csv'
REVIEW = 'review.csv'

DATA_FILES_CSV = [
    CATEGORY,
    GENRE,
    TITLES,
    GENRE_TITLE,
    USERS,
    COMMENTS,
    REVIEW,
]

STATIC_PATH = '/static/data/'
