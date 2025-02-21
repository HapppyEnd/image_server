import json
import os
import uuid
from io import BytesIO
from os.path import isfile

from aiohttp import web
from loguru import logger
from PIL import Image

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
IMAGES_DIR = 'images'
BASE_URL = 'http://localhost'
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

log_file = os.path.join('logs', 'app.log')
logger.add(
    log_file, format='{time:YYYY-MM-DD HH:mm:ss} {level}: {message}',
    level='INFO')

routes = web.RouteTableDef()


@routes.get('/')
async def get_main(request: web.Request) -> web.Response:
    """Обрабатывает GET-запросы на главную страницу."""
    logger.info(f'GET: {request.path}')
    with open(os.path.join('static', 'index.html'), encoding='utf-8') as file:
        html_content = file.read()
    return web.Response(
        status=200,
        text=html_content,
        content_type='text/html'
    )


@routes.route('*', '/{tail:.*}')
async def incorrect_url_handler(request: web.Request) -> web.Response:
    """Обрабатывает некорректные URL."""
    logger.error(f'Invalid path: {request.path}')
    return web.Response(status=404, text='Invalid URL')


async def check_file_uploaded(field) -> bool:
    """Проверяет, был ли загружен файл."""
    if not field:
        logger.warning('Upload failed. No file uploaded')
        return False
    return True


async def check_file_size(content_length: int, max_size: int) -> bool:
    """Проверяет, что размер файла не превышает допустимый."""
    if content_length > max_size:
        logger.error('Upload failed: File too large.',
                     content_length)
        return False
    return True


async def check_file_type(file_data: bytes) -> tuple:
    """
    Проверяет, что файл является изображением и имеет допустимое расширение.
    Возвращает кортеж (расширение, ошибка).
    """
    try:
        with Image.open(BytesIO(file_data)) as image:
            file_extension = image.format.lower() if image.format else None
            if file_extension not in ALLOWED_EXTENSIONS:
                logger.error(f'Unsupported file extension: {file_extension}')
                return file_extension, 'Unsupported file extension'
            return file_extension, None
    except Exception as e:
        logger.error(f'Unsupported file type: {e}')
        return None, 'Unsupported file type'


async def save_file(file_data: bytes, file_extension: set[str],
                    images_dir: str) -> str:
    """Сохраняет файл на диск и возвращает имя файла."""
    filename = f'{uuid.uuid4().hex}.{file_extension}'
    file_path = os.path.join(images_dir, filename)
    with Image.open(BytesIO(file_data)) as image:
        image.save(file_path)
    logger.info(f'File uploaded successfully: {file_path}')
    return filename


async def create_upload_response(filename: str) -> web.Response:
    """Формирует JSON-ответ об успешной загрузке файла."""
    response = {
        'message': 'File uploaded successfully',
        'file_url': f'{BASE_URL}/{IMAGES_DIR}/{filename}'
    }
    return web.Response(
        status=201,
        text=json.dumps(response),
        content_type='application/json'
    )


@routes.get('/api/images')
async def get_all_images(request: web.Request) -> web.Response:
    logger.info(f'GET: {request.path}')
    images = [file for file in os.listdir(IMAGES_DIR) if
              isfile(os.path.join(IMAGES_DIR, file))]
    logger.info(f'Images found: {images}')
    print(images)
    return web.Response(status=200, text=json.dumps({'images': images}),
                        content_type='application/json')


@routes.get('/images')
async def images_gallery_handler(request: web.Request) -> web.Response:
    """Отдает HTML-страницу с галереей изображений."""
    try:
        with open(os.path.join('static', 'images.html'), 'r',
                  encoding='utf-8') as file:
            html_content = file.read()
            logger.info(f'GET {request.path}')
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        logger.error(f'Error loading images gallery: {e}')
        return web.Response(status=500, text='Internal Server Error')


@routes.get('/upload')
async def upload_form_handler(request: web.Request) -> web.Response:
    """Отдает HTML-форму для загрузки изображений."""
    try:
        with open(os.path.join('static', 'upload.html'), 'r',
                  encoding='utf-8') as file:
            html_content = file.read()
            logger.info(f'GET {request.path}')
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        logger.error(f'Error loading upload form: {e}')
        return web.Response(status=500, text='Internal Server Error')


@routes.post('/upload')
async def post_handler(request: web.Request) -> web.Response:
    """Обрабатывает загрузку изображения."""
    try:
        reader = await request.multipart()
        field = await reader.next()

        if not await check_file_uploaded(field):
            return web.Response(status=400, text='No file uploaded')

        content_length = int(request.headers.get('Content-Length', 0))

        if not await check_file_size(content_length, MAX_FILE_SIZE):
            return web.Response(status=413,
                                text='Upload failed: File too large.')

        file_data = await field.read()
        file_extension, error = await check_file_type(file_data)

        if error:
            return web.Response(status=415, text=error)

        filename = await save_file(file_data, file_extension, IMAGES_DIR)
        return await create_upload_response(filename)
    except Exception as e:
        logger.error(f'Error during file upload: {e}')
        return web.Response(status=500, text='Internal Server Error')


async def init_app() -> web.Application:
    """Инициализирует приложение."""
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(init_app(), port=8000)
