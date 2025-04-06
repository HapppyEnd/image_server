import json
import os

from aiohttp import web
from loguru import logger

import constants
from db import Database
from utils import (check_file_size, check_file_type, check_file_uploaded,
                   create_upload_response, get_html_page, read_file_async,
                   save_file)

os.makedirs(constants.IMAGES_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

log_file = os.path.join('logs', constants.LOG_FILE)
logger.add(log_file, format=constants.LOG_FORMAT, level=constants.LOG_LEVEL)

routes = web.RouteTableDef()
db = Database()


async def init_db(app: web.Application):
    logger.info(constants.DB_CONNECT.format(db=constants.DATABASE_URL))
    await db.connect()
    await db.init_db()


@routes.get('/')
async def get_main(request: web.Request) -> web.Response:
    """GET requests to the main page.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with HTML content of the main page.
        """
    logger.info(constants.GET_REQUEST.format(request=request.path))

    html_content = await read_file_async(
        os.path.join('static', constants.INDEX_HTML))
    return web.Response(
        status=constants.HTTP_200_OK,
        text=html_content,
        content_type=constants.CONTENT_TYPE_HTML
    )


@routes.get('/api/images')
async def get_all_images(request: web.Request) -> web.Response:
    """Returns a list of all uploaded images.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with JSON list of images.
        """
    logger.info(
        constants.GET_REQUEST.format(
            request=request.query.get(constants.PAGE, 1)))
    try:
        page = int(request.query.get(constants.PAGE, 1))
        images_data = await db.get_images(page)
        if (images_data[constants.TOTAL_PAGES] < images_data[
            constants.PAGE] and
                images_data[constants.TOTAL_PAGES] != 0):
            last_page = images_data[constants.TOTAL_PAGES]
            return web.Response(status=constants.HTTP_404_NOT_FOUND,
                                text=json.dumps({
                                    constants.LAST_PAGE: last_page,
                                    constants.MSG: constants.PAGE_NOT_FOUND,
                                }))
        return web.Response(status=constants.HTTP_200_OK,
                            text=json.dumps(images_data),
                            content_type=constants.CONTENT_TYPE_JSON)
    except Exception as e:
        logger.error(constants.LOAD_IMAGE_GALLERY_ERROR.format(error=e))
        return web.Response(status=constants.HTTP_500_INTERNAL_SERVER_ERROR,
                            text=constants.LOAD_IMAGE_GALLERY_ERROR)


@routes.get('/images')
async def images_gallery_handler(request: web.Request) -> web.Response:
    """Serves HTML page with an image gallery.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with HTML content of the gallery page.
        """
    return await get_html_page(
        request, constants.IMAGES_HTML,
        error_message=constants.LOAD_IMAGE_GALLERY_ERROR)


@routes.get('/upload')
async def upload_form_handler(request: web.Request) -> web.Response:
    """Serves HTML form for uploading images.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with HTML content of the upload form."""
    return await get_html_page(request, constants.UPLOAD_HTML,
                               error_message=constants.UPLOAD_FORM_ERROR)


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
        logger.info(constants.POST_REQUEST.format(request=request.path))

        if not await check_file_uploaded(field):
            return web.Response(status=constants.HTTP_400_BAD_REQUEST,
                                text=constants.FILE_NOT_FOUND_RU)

        content_length = int(request.headers.get('Content-Length', 0))

        if not await check_file_size(content_length, constants.MAX_FILE_SIZE):
            return web.Response(
                status=constants.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                text=constants.FILE_TOO_LARGE_RU.format(size=content_length))

        file_data = await field.read()
        file_extension, error = await check_file_type(
            file_data,
            constants.ALLOWED_EXTENSIONS)

        if error:
            return web.Response(
                status=constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE, text=error)

        filename = await save_file(file_data, file_extension,
                                   constants.IMAGES_DIR)
        await db.insert_image(filename=filename,
                              original_name=field.filename,
                              size=content_length,
                              file_type=file_extension)
        return await create_upload_response(filename, constants.BASE_URL,
                                            constants.IMAGES_DIR)

    except Exception as e:
        logger.error(constants.UPLOAD_ERROR.format(error=e))
        return web.Response(status=constants.HTTP_500_INTERNAL_SERVER_ERROR,
                            text=constants.ERROR_500)


@routes.delete('/api/images/{id}')
async def delete_handler(request: web.Request) -> web.Response:
    try:
        image_id = request.match_info['id']
        success, filename = await db.delete_image(image_id)
        if not success:
            return web.Response(
                status=constants.HTTP_404_NOT_FOUND,
                text=constants.NOT_FOUND_IN_DB)
        if filename:
            file_path = os.path.join(constants.IMAGES_DIR, filename[0])
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError as e:
                logger.error(constants.DELETE_FILE_ERROR.format(error=e))

            return web.Response(
                status=constants.HTTP_200_OK,
                text=constants.DELETE_FILE_SUCCESS)
    except Exception as e:
        logger.error(constants.DELETE_FILE_ERROR.format(error=e))
        return web.Response(
            status=constants.HTTP_500_INTERNAL_SERVER_ERROR,
            text=constants.ERROR_500)


@routes.route('*', '/{tail:.*}')
async def incorrect_url_handler(request: web.Request) -> web.Response:
    """Handles invalid URLs.

    Args:
        request: Request object.
    Returns:
        web.Response: Response with 404 error."""
    logger.error(constants.INVALID_PATH.format(path=request.path))
    return web.Response(status=constants.HTTP_404_NOT_FOUND,
                        text=constants.INVALID_URL.format(path=request.path))


async def init_app() -> web.Application:
    """Initializes the application.

    Returns:
        web.Application: The application instance."""
    app = web.Application()
    app.add_routes(routes)
    await init_db(app)
    return app


if __name__ == '__main__':
    web.run_app(init_app(), port=constants.APP_PORT)
