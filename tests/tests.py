import io

import pytest
import pytest_asyncio
from aiohttp import FormData
from PIL import Image

import constants
from app import init_app


@pytest_asyncio.fixture
async def client(aiohttp_client):
    """Creates aiohttp client for testing.

    Initializes the application and returns a client instance
    that can be used to make requests to the application during tests.
    """
    app = await init_app()
    return await aiohttp_client(app)


@pytest_asyncio.fixture
def form_data():
    """Creates FormData object for file uploads.

    Returns a function that can be used to create FormData
    with specified file content, filename, and content type.

    Usage:
        form = form_data(file_content, filename, content_type)
    """

    def create_form_data(file_content, filename, content_type):
        form = FormData()
        form.add_field('file', file_content, filename=filename,
                       content_type=content_type)
        return form

    return create_form_data


@pytest.mark.asyncio
async def test_get_main_page(client):
    """Tests GET main page.

        Checks that the main page returns status 200 and has
        the correct Content-Type header.
        """
    response = await client.get('/')
    assert response.status == 200
    assert 'text/html' in response.headers['Content-Type']


@pytest.mark.asyncio
async def test_get_all_images(client):
    """Tests GET all images.

    Checks that the API for all images returns status 200
    and contains the 'images' key in the JSON response.
    """
    response = await client.get('/api/images')
    assert response.status == 200
    data = await response.json()
    assert 'images' in data


@pytest.mark.asyncio
async def test_images_gallery(client):
    """Tests displaying the images gallery.

    Checks that the images gallery page returns status 200
    and has the correct Content-Type header.
    """
    response = await client.get('/images')
    print(response)
    assert response.status == 200
    assert 'text/html' in response.headers['Content-Type']


@pytest.mark.asyncio
async def test_upload_form(client):
    """Tests the upload form.

    Checks that the image upload form returns status 200
    and has the correct Content-Type header.
    """
    response = await client.get('/upload')
    assert response.status == 200
    assert 'text/html' in response.headers['Content-Type']


@pytest.mark.asyncio
async def test_upload_image_success(client, form_data):
    """Tests successful image upload.

    Checks that uploading a valid image returns status 201
    and contains the URL of the uploaded file.
    """
    image = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    form = form_data(img_byte_arr, 'test.png', 'image/png')
    response = await client.post('/upload', data=form)
    assert response.status == 201

    data = await response.json()
    assert 'file_url' in data


@pytest.mark.asyncio
async def test_upload_image_too_large(client, form_data):
    """Tests uploading an image that exceeds the allowed size.

   Checks that uploading a file that exceeds the maximum size
   returns status 413 (Payload Too Large).
   """
    large_image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * (
            constants.MAX_FILE_SIZE + 1)
    form = form_data(large_image_data, 'large.png', 'image/png')
    response = await client.post('/upload', data=form)
    assert response.status == 413


@pytest.mark.asyncio
async def test_upload_unsupported_file_type(client, form_data):
    """Tests uploading an unsupported file type.

   Checks that uploading a file of an unsupported type returns
   status 415 (Unsupported Media Type).
   """
    unsupported_image_data = b'This is not an image'
    form = form_data(unsupported_image_data, 'test.txt', 'text/plain')
    response = await client.post('/upload', data=form)
    assert response.status == 415
