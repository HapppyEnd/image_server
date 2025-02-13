import json
import logging
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from mimetypes import guess_type

from PIL import Image

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)
CONTENT_LENGTH = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
PORT = 8000


class ImageHostingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Welcome to the Image Hosting Service!')
            logging.info('GET request to /')
        elif self.path.startswith('/images/'):
            file_path = self.path[1:]  # Убираем первый слэш
            if os.path.exists(file_path):
                mime_type, _ = guess_type(file_path)
                if mime_type and mime_type.startswith('image/'):
                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.end_headers()
                    with open(file_path, 'rb') as image:
                        self.wfile.write(image.read())
                    logging.info(f'Served image: {file_path}')
                else:
                    self.send_error(415, 'Unsupported Media Type')
                    logging.error(f'Unsupported file type: {file_path}')
            else:
                self.send_error(404, 'File not found')
                logging.error(f'File not found: {file_path}')
        else:
            self.send_error(404, 'Not found')
            logging.error(f'Invalid path: {self.path}')

    def do_POST(self):
        if self.path == '/upload':
            try:
                content_length = int(self.headers.get('Content-Length'))
                if content_length > CONTENT_LENGTH:  # 5 МБ
                    self.send_error(413, 'File too large')
                    logging.error('File too large')
                    return

                file_data = self.rfile.read(content_length)

                # Проверяем, что файл является изображением с помощью Pillow
                try:
                    image = Image.open(BytesIO(file_data))
                    image.verify()  # Проверка, что файл является изображением
                except Exception:
                    self.send_error(415, 'Unsupported file type')
                    logging.error('Unsupported file type')
                    return

                # Генерация уникального имени файла
                file_extension = image.format.lower()
                if file_extension not in ALLOWED_EXTENSIONS:
                    self.send_error(415, 'Unsupported file extension')
                    logging.error(
                        f'Unsupported file extension: {file_extension}')
                    return

                filename = f'{uuid.uuid4().hex}.{file_extension}'
                file_path = f'images/{filename}'

                # Сохранение файла
                os.makedirs('images', exist_ok=True)
                with open(file_path, 'wb') as file:
                    file.write(file_data)

                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'message': 'File uploaded successfully',
                    'file_url': f'/images/{filename}'
                }
                self.wfile.write(json.dumps(response).encode())
                logging.info(f'File uploaded: {file_path}')
            except Exception as e:
                self.send_error(500, 'Internal Server Error')
                logging.error(f'Error during file upload: {e}')
        else:
            self.send_error(404, 'Not found')
            logging.error(f'Invalid path: {self.path}')


def run():
    # Проверка и создание директории для изображений
    os.makedirs('images', exist_ok=True)
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, ImageHostingHandler)
    logging.info(f'Starting server on port {PORT}')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
