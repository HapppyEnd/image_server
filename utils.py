import json
import os
import uuid
from io import BytesIO

import aiofiles
from aiohttp import web
from loguru import logger
from PIL import Image

log_file = os.path.join('logs', 'app.log')
logger.add(
    log_file, format='{time:YYYY-MM-DD HH:mm:ss} {level}: {message}',
    level='INFO')


async def read_file_async(file_path: str) -> str:
    """Асинхронно читает файл и возвращает его содержимое."""
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        return await file.read()


async def check_file_uploaded(field) -> bool:
    """Проверяет, был ли загружен файл."""
    if not field:
        logger.warning('Upload failed. No file uploaded')
        return False
    return True


async def check_file_size(content_length: int, max_file_size: int) -> bool:
    """Проверяет, что размер файла не превышает допустимый."""
    if content_length > max_file_size:
        logger.error('Upload failed: File too large.',
                     content_length)
        return False
    return True


async def check_file_type(file_data: bytes,
                          allowed_extensions: tuple[str, ...]) -> tuple:
    """
    Проверяет, что файл является изображением и имеет допустимое расширение.
    Возвращает кортеж (расширение, ошибка).
    """
    try:
        with Image.open(BytesIO(file_data)) as image:
            file_extension = image.format.lower() if image.format else None
            if file_extension not in allowed_extensions:
                logger.error(f'Unsupported file extension: {file_extension}')
                return file_extension, 'Unsupported file extension'
            return file_extension, None
    except Exception as e:
        logger.error(f'Unsupported file type: {e}')
        return None, 'Unsupported file type'


async def save_file(file_data: bytes, file_extension: str,
                    images_dir: str
                    ) -> str:
    """Сохраняет файл на диск и возвращает имя файла."""
    filename = f'{uuid.uuid4().hex}.{file_extension}'
    file_path = os.path.join(images_dir, filename)
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(file_data)
    logger.info(f'File uploaded successfully: {file_path}')
    return filename


async def create_upload_response(filename: str, base_url: str,
                                 images_dir: str) -> web.Response:
    """Формирует JSON-ответ об успешной загрузке файла."""
    response = {
        'message': 'File uploaded successfully',
        'file_url': f'{base_url}/{images_dir}/{filename}'
    }
    return web.Response(
        status=201,
        text=json.dumps(response),
        content_type='application/json'
    )
