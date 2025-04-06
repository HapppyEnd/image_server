import os

from dotenv import load_dotenv

load_dotenv()

# messages
FILE_NOT_FOUND = 'File not found: {file_path}'
FILE_NOT_FOUND_RU = 'Файл не найден'
UPLOAD_FAILED_NO_FILE = 'Upload failed. No file uploaded'
FILE_TOO_LARGE = 'Upload failed: File too large. Size: {size} bytes'
FILE_TOO_LARGE_RU = "Загрузка не удалась, файл слишком большой: {size} байт"
UNSUPPORTED_EXTENSION = 'Unsupported file extension: {extension}'
UNSUPPORTED_EXTENSION_RU = 'Неподдерживаемое расширение файла {file_extension}'
UNSUPPORTED_FILE_TYPE = 'Unsupported file type: {error}'
LOAD_IMAGE_GALLERY_ERROR = 'Error loading images gallery: {error}'
UPLOAD_FORM_ERROR = 'Error loading upload form: {error}'
UPLOAD_ERROR = 'Error during file upload: {error}'
UNSUPPORTED_FILE_TYPE_RU = 'Неподдерживаемый тип файла'
FILE_UPLOAD_SUCCESS = 'File uploaded successfully: {file_path}'
UPLOAD_SUCCESS_MESSAGE = 'Изображение успешно загружено'
INVALID_URL = 'Invalid URL: {path}'
ERROR_500 = 'Ошибка сервера'
INVALID_PATH = "Invalid path: {path}"
DELETE_FILE_ERROR = 'Failed to delete file {error}'
DELETE_FILE_SUCCESS = 'File deleted successfully: {id}'

# logs
LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss} {level}: {message}'
LOG_LEVEL = 'INFO'
LOG_FILE = 'app.log'
LOG_DIR = 'logs'

# images
IMAGES_DIR = 'images'

# HTML
INDEX_HTML = 'index.html'
IMAGES_HTML = 'images/images.html'
UPLOAD_HTML = 'upload.html'

# HTTP status
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Content-type
CONTENT_TYPE_HTML = "text/html"
CONTENT_TYPE_JSON = "application/json"

# .env
ALLOWED_EXTENSIONS = tuple(os.getenv('ALLOWED_EXTENSIONS').split(','))
APP_PORT = int(os.getenv('APP_PORT'))
BASE_URL = os.getenv('BASE_URL')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE'))
DATABASE_URL = os.getenv('DATABASE_URL')

# Requests
GET_REQUEST = 'GET: {request}'
POST_REQUEST = 'POST: {request}'

# Pages
ITEMS_PER_PAGE = 1

# Database
DB_POOL_MIN_SIZE = 1
DB_POOL_MAX_SIZE = 10

ERROR_DB_CONNECTION = 'Database connection error {error}'
ERROR_DB_OPERATION = 'Database operation failed {error}'
DB_POOL_SUCCESS = 'Database pool created successfully'
DB_POOL_CLOSE_SUCCESS = 'Database pool closed successfully'
DISCONNECT_FAILED = 'Failed to disconnect from database {error}'
CREATE_TABLE_SUCCESS = 'Database tables initialized'
CREATE_TABLE_ERROR = 'Database table initialization failed {error}'
DB_CONNECTION_NOT_ESTABLISH = 'Database connection is not established'
IMG_INSERT_FAILED = 'Image insert failed {error}'
IMG_DELETE_FAILED = 'Image deletion failed {error}'
IMG_INSERT_SUCCESS = 'Image inserted with ID: {image_id}'
IMG_DELETE_SUCCESS = 'Image deleted successfully: {filename}'
FAIL_TO_FETCH_IMG = 'Failed to fetch images: {error}'
NOT_FOUND_IN_DB = 'Image not found in database'
DB_CONNECT = 'Connected to database: {db}'