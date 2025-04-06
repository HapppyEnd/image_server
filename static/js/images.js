/**
 * Fetches and displays a gallery of images from the server with pagination.
 */
const gallery = document.getElementById('gallery');
const paginationContainer = document.createElement('div');
paginationContainer.id = 'pagination';
paginationContainer.className = 'pagination'; // Добавляем класс для стилизации
gallery.after(paginationContainer);

let currentPage = 1;

const handleDelete = (id) => {
    fetch(`/api/images/${id}`, {
        method: 'DELETE'
    }).then(() => {
        fetchImages(currentPage);
    });
}

// Основная функция загрузки изображений
async function fetchImages(page = 1) {
    try {
        const response = await fetch(`/api/images?page=${page}`);
        if (response.status === 404) {
            const error404 = await response.json();
            document.location.href = `/images?page=${error404.last_page}`
        }
        const data = await response.json();

        gallery.innerHTML = '';
        console.log(data.images)
        if (!data.images.length) {
            const notFoundMessage = document.createElement("div")
            notFoundMessage.innerHTML = "В галерее еще нет изображений."
            gallery.className = "gallery notFoundMessage"

            gallery.appendChild(notFoundMessage)
        } else {
            data.images.forEach(item => gallery.appendChild(card(item)));
        }

        renderPagination(page, data.total_pages || 1);
        currentPage = page;

        history.pushState(null, null, `?page=${page}`);
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

// Функция рендеринга пагинации с иконками
function renderPagination(currentPage, totalPages) {
    paginationContainer.innerHTML = '';

    // Первая страница
    if (currentPage > 1) {
        const firstBtn = createPaginationButton('<<', () => fetchImages(1));
        firstBtn.className = 'pagination-first';
        firstBtn.title = 'Первая страница';
        paginationContainer.appendChild(firstBtn);
    }

    // Предыдущая страница
    if (currentPage > 1) {
        const prevBtn = createPaginationButton('<', () => fetchImages(currentPage - 1));
        prevBtn.className = 'pagination-prev';
        prevBtn.title = 'Предыдущая страница';
        paginationContainer.appendChild(prevBtn);
    }

    // Текущая страница и ближайшие
    const startPage = Math.max(1, currentPage - 1);
    const endPage = Math.min(totalPages, currentPage + 1);

    if (startPage > 1) {
        const dots = document.createElement('span');
        dots.className = 'pagination-dots';
        dots.textContent = '...';
        paginationContainer.appendChild(dots);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = createPaginationButton(i, () => fetchImages(i));
        pageBtn.className = 'pagination-page';
        if (i === currentPage) {
            pageBtn.classList.add('active');
        }
        paginationContainer.appendChild(pageBtn);
    }

    if (endPage < totalPages) {
        const dots = document.createElement('span');
        dots.className = 'pagination-dots';
        dots.textContent = '...';
        paginationContainer.appendChild(dots);
    }

    // Следующая страница
    if (currentPage < totalPages) {
        const nextBtn = createPaginationButton('>', () => fetchImages(currentPage + 1));
        nextBtn.className = 'pagination-next';
        nextBtn.title = 'Следующая страница';
        paginationContainer.appendChild(nextBtn);
    }

    // Последняя страница
    if (currentPage < totalPages) {
        const lastBtn = createPaginationButton('>>', () => fetchImages(totalPages));
        lastBtn.className = 'pagination-last';
        lastBtn.title = 'Последняя страница';
        paginationContainer.appendChild(lastBtn);
    }
}

// Вспомогательная функция для создания кнопок
function createPaginationButton(text, onClick) {
    const button = document.createElement('button');
    button.innerHTML = text;
    button.addEventListener('click', onClick);
    return button;
}

// Функция создания карточки (без изменений)
const card = (item) => {
    const card = document.createElement('div');
    card.className = 'card';

    const link = document.createElement('a');
    link.href = `/images/${item.filename}`;

    const imgContainer = document.createElement('div');
    imgContainer.className = 'imgContainer';

    const img = document.createElement('img');
    img.src = `/images/${item.filename}`;
    img.alt = item.filename;
    img.className = 'img';

    const textContainer = document.createElement('div');
    textContainer.className = 'textContainer';

    const name = document.createElement('div');
    name.className = 'size cardText';
    name.innerText = `Имя: ${item.original_name.split('.')[0]}`;

    const type = document.createElement('div');
    type.className = 'size cardText';
    type.innerText = `Тип: ${item.file_type}`;

    const size = document.createElement('div');
    size.className = 'size cardText';
    size.innerText = `Размер: ${item.size_kb}Кб`;

    const date = document.createElement('div');
    date.innerText = `${item.upload_date}`;
    date.className = "date cardText"

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'buttonContainer';

    const viewButton = document.createElement('button');
    viewButton.textContent = "Посмотреть";
    viewButton.className = "submit"
    link.appendChild(viewButton);

    const btn = document.createElement('button');
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        handleDelete(item.id);
    });
    const im = `<svg width="20" height="20" viewBox="0 0 427 427" xmlns="http://www.w3.org/2000/svg">
  <path d="M232.4 154.7c-5.5 0-10 4.5-10 10v189c0 5.5 4.5 10 10 10 5.5 0 10-4.5 10-10v-189c0-5.5-4.5-10-10-10z" fill="none" stroke="white" stroke-width="10"/>
  <path d="M114.4 154.7c-5.5 0-10 4.5-10 10v189c0 5.5 4.5 10 10 10 5.5 0 10-4.5 10-10v-189c0-5.5-4.5-10-10-10z" fill="none" stroke="white" stroke-width="10"/>
  <path d="M28.4 127.1v246.4c0 14.6 5.3 28.2 14.7 38 9.3 9.8 22.2 15.4 35.7 15.4h189.2c13.5 0 26.4-5.6 35.7-15.4 9.3-9.8 14.7-23.5 14.7-38V127.1c18.5-4.9 30.6-22.8 28.1-41.9-2.5-19-18.7-33.3-37.9-33.3h-51.2v-12.5c.1-10.5-4.1-20.6-11.5-28-7.4-7.4-17.6-11.6-28.1-11.5h-88.8c-10.5-.1-20.6 4-28.1 11.5-7.4 7.4-11.6 17.5-11.5 28v12.5h-51.2c-19.2 0-35.4 14.2-37.9 33.3-2.5 19 9.5 36.9 28.1 41.9zm239.6 279.9h-189.2c-17.1 0-30.4-14.7-30.4-33.5v-245.5h250v245.5c0 18.8-13.3 33.5-30.4 33.5zm-158.6-367.5c-.1-5.2 2-10.2 5.7-13.9 3.7-3.7 8.7-5.7 13.9-5.6h88.8c5.2-.1 10.2 1.9 13.9 5.6 3.7 3.7 5.7 8.7 5.7 13.9v12.5h-128zm-71.2 32.5h270.4c9.9 0 18 8.1 18 18s-8.1 18-18 18h-270.4c-9.9 0-18-8.1-18-18s8.1-18 18-18z" fill="none" stroke="white" stroke-width="10"/>
  <path d="M173.4 154.7c-5.5 0-10 4.5-10 10v189c0 5.5 4.5 10 10 10 5.5 0 10-4.5 10-10v-189c0-5.5-4.5-10-10-10z" fill="none" stroke="white" stroke-width="10"/>
</svg>`
    btn.innerHTML = im;
    btn.className = "submit"

    textContainer.appendChild(name);
    textContainer.appendChild(type);
    textContainer.appendChild(size);
    textContainer.appendChild(date);
    buttonContainer.appendChild(link);
    buttonContainer.appendChild(btn);

    card.appendChild(imgContainer);
    card.appendChild(textContainer);
    card.appendChild(buttonContainer);
    imgContainer.appendChild(img);

    return card;
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page')) || 1;
    fetchImages(page);
});

window.addEventListener('popstate', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page')) || 1;
    fetchImages(page);
});