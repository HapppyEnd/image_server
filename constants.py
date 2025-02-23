from dotenv import load_dotenv
import os

load_dotenv()

# Messages
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
INVALID_URL = 'Invalid URL'
ERROR_505 = 'Ошибка сервера'
INVALID_PATH = "Invalid path: {path}"

# logs
LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss} {level}: {message}'
LOG_LEVEL = 'INFO'
LOG_FILE = 'app.log'
LOG_DIR = 'logs'

# Directories
IMAGES_DIR = 'images'

# HTML
INDEX_HTML = "index.html"
IMAGES_HTML = "images.html"
UPLOAD_HTML = "upload.html"

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
BASE_URL = os.getenv('BASE_URL')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE'))

# Port
APP_PORT = 8000

# Request
GET_REQUEST = 'GET: {request}'