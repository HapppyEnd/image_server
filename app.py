import json
import logging
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from mimetypes import guess_type
from typing import Any

from PIL import Image

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
IMAGES_DIR = 'images'


class ImageHostingHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/':
            self._send_response(200, 'Welcome to the Image Hosting Service!',
                                content_type='text/html')
            logging.info('GET request to /')
        elif self.path.startswith('/images/'):
            file_path = self.path[1:]  # Убираем первый слэш
            self._serve_image(file_path)
        else:
            self._send_error(404, 'Not found')
            logging.error(f'Invalid path: {self.path}')

    def do_POST(self) -> None:
        if self.path == '/upload':
            self._handle_upload()
        else:
            self._send_error(404, 'Not found')
            logging.error(f'Invalid path: {self.path}')

    def _serve_image(self, file_path: str) -> None:
        """Отдает изображение по запрошенному пути."""
        if not os.path.exists(file_path):
            self._send_error(404, 'File not found')
            logging.error(f'File not found: {file_path}')
            return

        mime_type, _ = guess_type(file_path)
        if not mime_type or not mime_type.startswith('image/'):
            self._send_error(415, 'Unsupported Media Type')
            logging.error(f'Unsupported file type: {file_path}')
            return

        try:
            with open(file_path, 'rb') as image:
                self._send_response(200, image.read(), content_type=mime_type)
            logging.info(f'Served image: {file_path}')
        except Exception as e:
            self._send_error(500, 'Internal Server Error')
            logging.error(f'Error serving image: {e}')

    def _handle_upload(self) -> None:
        """Обрабатывает загрузку изображения."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > MAX_FILE_SIZE:
                self._send_error(413, 'File too large')
                logging.error('File too large')
                return

            file_data = self.rfile.read(content_length)

            # Проверяем, что файл является изображением
            try:
                image = Image.open(BytesIO(file_data))
                file_extension = image.format.lower() if image.format else None
                if (not file_extension or file_extension
                        not in ALLOWED_EXTENSIONS):
                    self._send_error(415, 'Unsupported file extension')
                    logging.error(
                        f'Unsupported file extension: {file_extension}')
                    return

                # Генерация уникального имени файла
                filename = f'{uuid.uuid4().hex}.{file_extension}'
                file_path = os.path.join(IMAGES_DIR, filename)

                # Сохранение файла
                os.makedirs(IMAGES_DIR, exist_ok=True)
                image.save(file_path)
                image.close()

                # Отправляем ответ
                response = {
                    'message': 'File uploaded successfully',
                    'file_url': f'/images/{filename}'
                }
                self._send_response(201, response,
                                    content_type='application/json')
                logging.info(f'File uploaded: {file_path}')
            except Exception as e:
                self._send_error(415, 'Unsupported file type')
                logging.error(f'Unsupported file type: {e}')
        except Exception as e:
            self._send_error(500, 'Internal Server Error')
            logging.error(f'Error during file upload: {e}')

    def _send_response(self, status_code: int, content: Any,
                       content_type: str = 'text/plain') -> None:
        """Отправляет HTTP-ответ с указанным статусом и содержимым."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        if isinstance(content, (dict, list)):
            content = json.dumps(content).encode()
        elif isinstance(content, str):
            content = content.encode()
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_error(self, status_code: int, message: str) -> None:
        """Отправляет HTTP-ошибку с указанным статусом и сообщением."""
        self.send_error(status_code, message)


def run() -> None:
    """Запускает сервер."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ImageHostingHandler)
    logging.info('Starting server on port 8000')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
