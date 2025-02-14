import json
import logging
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from mimetypes import guess_type
from typing import Any

from PIL import Image

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
            self.response_handler(200, 'Welcome to the Image Hosting Service!',
                                  content_type='text/html')
            logging.info('GET request to /')
        elif self.path.startswith('/images/'):
            file_path = self.path[1:]  # Убираем первый слэш
            self.get_image(file_path)
        else:
            self.error_handler(404, 'Not found')
            logging.error(f'Invalid path: {self.path}')

    def do_POST(self) -> None:
        if self.path == '/upload':
            self.image_upload_handler()
        else:
            self.error_handler(404, 'Not found')
            logging.error(f'Invalid path: {self.path}')

    def get_image(self, file_path: str) -> None:
        """Отдает изображение по запрошенному пути."""
        if not os.path.exists(file_path):
            self.error_handler(404, 'File not found')
            logging.error(f'File not found: {file_path}')
            return

        mime_type, _ = guess_type(file_path)
        if not mime_type or not mime_type.startswith('image/'):
            self.error_handler(415, 'Unsupported Media Type')
            logging.error(f'Unsupported file type: {file_path}')
            return

        try:
            with open(file_path, 'rb') as image:
                self.response_handler(200, image.read(),
                                      content_type=mime_type)
            logging.info(f'Served image: {file_path}')
        except Exception as e:
            self.error_handler(500, 'Internal Server Error')
            logging.error(f'Error serving image: {e}')

    def image_upload_handler(self) -> None:
        """Обрабатывает загрузку изображения."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > MAX_FILE_SIZE:
                self.error_handler(413, 'File too large')
                logging.error('Upload failed: File too large. Size: %d bytes',
                              content_length)
                return

            file_data = self.rfile.read(content_length)

            # Проверяем, что файл является изображением
            try:
                with Image.open(BytesIO(file_data)) as image:
                    file_extension = image.format.lower() if image.format else None
                    if (file_extension is None or file_extension
                            not in ALLOWED_EXTENSIONS):
                        self.error_handler(415, 'Unsupported file extension')
                        logging.error(
                            'Upload failed: Unsupported file extension. Received: %s',
                            file_extension)
                        return

                    # Генерация уникального имени файла
                    filename = f'{uuid.uuid4().hex}.{file_extension}'
                    file_path = os.path.join(IMAGES_DIR, filename)

                    # Сохранение файла
                    image.save(file_path)

                    # Отправляем ответ
                    response = {
                        'message': 'File uploaded successfully',
                        'file_url': f'/images/{filename}'
                    }
                    self.response_handler(201, response,
                                          content_type='application/json')
                    logging.info(f'File uploaded: {file_path}')
            except Exception as e:
                self.error_handler(415, 'Unsupported file type')
                logging.error(
                    'Upload failed: Unsupported file type. Error: %s', str(e))
        except Exception as e:
            self.error_handler(500, 'Internal Server Error')
            logging.error('Error during file upload: %s', str(e))

    def response_handler(self, status_code: int, content: Any,
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

    def error_handler(self, status_code: int, message: str) -> None:
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
