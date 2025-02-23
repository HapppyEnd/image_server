import json
import os
import uuid
from io import BytesIO

import aiofiles
from aiohttp import web
from loguru import logger
from PIL import Image

import constants

log_file = os.path.join('logs', constants.LOG_FILE)
logger.add(log_file, format=constants.LOG_FORMAT, level=constants.LOG_LEVEL)


async def read_file_async(file_path: str) -> str:
    """Read file and returns its content.

    Args:
        file_path: The path to the file.
    Returns:
        str: The content of the file.
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            constants.FILE_NOT_FOUND.format(file_path=file_path))
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        return await file.read()


async def check_file_uploaded(field) -> bool:
    """Checks if a file has been uploaded.

    Args:
        field: The file field from a multipart request.
    Returns:
        bool: True if a file was uploaded, otherwise False.
        """
    if not field:
        logger.warning(constants.UPLOAD_FAILED_NO_FILE)
        return False
    return True


async def check_file_size(content_length: int, max_file_size: int) -> bool:
    """Checks the file size.

    Args:
        content_length: The size of the file in bytes.
        max_file_size: The maximum allowed file size in bytes.
    Returns:
        bool: True if the file size is within the limit, otherwise False.
        """
    if content_length > max_file_size:
        logger.error(
            constants.FILE_TOO_LARGE.format(size=content_length),
            content_length)
        return False
    return True


async def check_file_type(file_data: bytes,
                          allowed_extensions: tuple[str, ...]) -> tuple:
    """
    Checks if the file is an image and has an allowed extension.

    Args:
        file_data: Byte content of the file.
        allowed_extensions: Tuple of allowed file extensions.
    Returns:
        tuple: tuple (extension, error).
            If the file is valid, returns (extension, None).
            If the file is invalid, returns (None, error message).
    """
    try:
        with Image.open(BytesIO(file_data)) as image:
            file_extension = image.format.lower() if image.format else None
            if file_extension not in allowed_extensions:
                logger.error(constants.UNSUPPORTED_EXTENSION.format(
                    extension=file_extension))
                return None, constants.UNSUPPORTED_EXTENSION_RU.format(
                    file_extension=file_extension)
            return file_extension, None
    except Exception as e:
        logger.error(constants.UNSUPPORTED_FILE_TYPE.format(error=e))
        return None, constants.UNSUPPORTED_FILE_TYPE_RU


async def save_file(file_data: bytes, file_extension: str,
                    images_dir: str
                    ) -> str:
    """Saves a file to disk and returns the filename.

    Args:
        file_data: The byte content of the file.
        file_extension: The file extension (e.g., "jpg", "png").
        images_dir: The directory to save the file in.
    Returns:
        str: The name of the saved file.
        """
    filename = f'{uuid.uuid4().hex}.{file_extension}'
    file_path = os.path.join(images_dir, filename)
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(file_data)
    logger.info(constants.FILE_UPLOAD_SUCCESS.format(file_path=file_path))
    return filename


async def create_upload_response(filename: str, base_url: str,
                                 images_dir: str) -> web.Response:
    """Creates a JSON response for a successful file upload.

    Args:
        filename: The name of the file.
        base_url: The base URL.
        images_dir: The directory containing the images.
    Returns:
        web.Response: A response with JSON data.
        """
    response = {
        'message': constants.UPLOAD_SUCCESS_MESSAGE,
        'file_url': f'{base_url}/{images_dir}/{filename}'
    }
    return web.Response(
        status=constants.HTTP_201_CREATED,
        text=json.dumps(response),
        content_type=constants.CONTENT_TYPE_JSON
    )
