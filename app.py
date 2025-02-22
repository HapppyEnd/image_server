import json
import os
from os.path import isfile

from aiohttp import web
from dotenv import load_dotenv
from loguru import logger

from utils import (check_file_size, check_file_type, check_file_uploaded,
                   create_upload_response, read_file_async, save_file)

load_dotenv()

ALLOWED_EXTENSIONS = tuple(os.getenv('ALLOWED_EXTENSIONS').split(','))
IMAGES_DIR = os.getenv('IMAGES_DIR')
BASE_URL = os.getenv('BASE_URL')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE'))

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

log_file = os.path.join('logs', 'app.log')
logger.add(
    log_file, format='{time:YYYY-MM-DD HH:mm:ss} {level}: {message}',
    level='INFO')

routes = web.RouteTableDef()


@routes.get('/')
async def get_main(request: web.Request) -> web.Response:
    """GET requests to the main page.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with HTML content of the main page.
        """
    logger.info(f'GET: {request.path}')

    html_content = await read_file_async(os.path.join('static', 'index.html'))
    return web.Response(
        status=200,
        text=html_content,
        content_type='text/html'
    )


@routes.get('/api/images')
async def get_all_images(request: web.Request) -> web.Response:
    """Returns a list of all uploaded images.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with JSON list of images.
        """
    logger.info(f'GET: {request.path}')
    images = [file for file in os.listdir(IMAGES_DIR) if
              isfile(os.path.join(IMAGES_DIR, file))]
    return web.Response(status=200, text=json.dumps({'images': images}),
                        content_type='application/json')


@routes.get('/images')
async def images_gallery_handler(request: web.Request) -> web.Response:
    """Serves HTML page with an image gallery.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with HTML content of the gallery page.
        """
    try:

        html_content = await read_file_async(
            os.path.join('static', 'images.html'))
        logger.info(f'GET {request.path}')
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        logger.error(f'Error loading images gallery: {e}')
        return web.Response(status=500, text='Internal Server Error')


@routes.get('/upload')
async def upload_form_handler(request: web.Request) -> web.Response:
    """Serves HTML form for uploading images.

    Args:
        request: Request object.

    Returns:
        web.Response: Response with HTML content of the upload form."""
    try:
        html_content = await read_file_async(
            os.path.join('static', 'upload.html'))
        logger.info(f'GET {request.path}')
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        logger.error(f'Error loading upload form: {e}')
        return web.Response(status=500, text='Internal Server Error')


@routes.post('/upload')
async def post_handler(request: web.Request) -> web.Response:
    """ Handles the upload of an image.

    Args:
        request: Request object.

    Returns:
        web.Response: Response with the result of the upload."""
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
        file_extension, error = await check_file_type(file_data,
                                                      ALLOWED_EXTENSIONS)

        if error:
            return web.Response(status=415, text=error)

        filename = await save_file(file_data, file_extension, IMAGES_DIR)
        return await create_upload_response(filename, BASE_URL, IMAGES_DIR)
    except Exception as e:
        logger.error(f'Error during file upload: {e}')
        return web.Response(status=500, text='Internal Server Error')


@routes.route('*', '/{tail:.*}')
async def incorrect_url_handler(request: web.Request) -> web.Response:
    """Handles invalid URLs.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with 404 error."""
    logger.error(f'Invalid path: {request.path}')
    return web.Response(status=404, text='Invalid URL')


async def init_app() -> web.Application:
    """Initializes the application.

    Returns:
        web.Application: The application instance."""
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(init_app(), port=8000)
