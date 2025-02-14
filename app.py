import json
import logging
import os
import uuid
from io import BytesIO

from aiohttp import web
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS')
IMAGES_DIR = os.getenv('IMAGES_DIR')
BASE_URL = os.getenv('BASE_URL')
MAX_FILE_SIZE = 5 * 1024 * 1024
LOG_DIR = os.getenv('LOG_DIR')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)

routes = web.RouteTableDef()


@routes.get('/')
async def get_handler(request: web.Request):
    """Обрабатывает GET-запросы."""

    return web.Response(status=200,
                        text='Welcome to the Image Hosting Service!',
                        content_type='text/html')


@routes.get('/images/{tail:.*}')
async def image_handler(request: web.Request):
    logging.error(f'Invalid path: {request.path}')
    return web.Response(status=404, text='Not Found URL for BACKEND')


@routes.route('*', '/{tail:.*}')
async def incorrect_url_handler(request: web.Request):
    logging.error(f'Invalid path: {request.path}')
    return web.Response(status=404, text='Invalid URL')


@routes.post('/upload')
async def post_handler(request: web.Request) -> web.Response:
    """Обрабатывает загрузку изображения."""
    try:
        reader = await request.multipart()
        field = await reader.next()

        if field is None:
            return web.Response(status=400, text='No file uploaded')

        content_length = int(request.headers.get('Content-Length', 0))
        if content_length > MAX_FILE_SIZE:
            logging.error('Upload failed: File too large. Size: %d bytes',
                          content_length)
            return web.Response(status=413,
                                text='Upload failed: File too large.')

        # Чтение данных файла
        file_data = await field.read()

        # Проверяем, что файл является изображением
        try:
            with Image.open(BytesIO(file_data)) as image:
                file_extension = image.format.lower() if image.format else None
                if file_extension not in ALLOWED_EXTENSIONS:
                    logging.error(
                        f'Unsupported file extension: {file_extension}')
                    return web.Response(status=415,
                                        text='Unsupported file extension')

                # Генерация уникального имени файла
                filename = f'{uuid.uuid4().hex}.{file_extension}'
                file_path = os.path.join(IMAGES_DIR, filename)
                image.save(file_path)

                # Отправляем ответ
                response = {
                    'message': 'File uploaded successfully',
                    'file_url': f'{BASE_URL}/{IMAGES_DIR}/{filename}'
                }
                logging.info(f'File uploaded: {file_path}')
                return web.Response(
                    status=201,
                    text=json.dumps(response),
                    content_type='application/json')
        except Exception as e:
            logging.error(f'Unsupported file type: {e}')
            return web.Response(status=415, text='Unsupported file type')
    except Exception as e:
        logging.error(f'Error during file upload: {e}')
        return web.Response(status=500, text='Internal Server Error')


async def init_app() -> web.Application:
    """Инициализирует приложение."""
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    os.makedirs(IMAGES_DIR, exist_ok=True)
    web.run_app(init_app(), port=8000)
