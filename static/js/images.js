/**
 * Fetches and displays a gallery of images from the server with pagination.
 */
const gallery = document.getElementById('gallery');
const paginationContainer = document.createElement('div');
paginationContainer.id = 'pagination';
paginationContainer.className = 'pagination'; // Добавляем класс для стилизации
gallery.after(paginationContainer);

let currentPage = 1;
const imagesPerPage = 10;

const handleDelete = (id) => {
    fetch(`/api/images/${id}`, {
        method: 'DELETE'
    }).then(() => {
        alert("Изображение удалено");
        fetchImages(currentPage);
    });
}

// Основная функция загрузки изображений
async function fetchImages(page = 1) {
    try {
        const response = await fetch(`/api/images?page=${page}`);
        const data = await response.json();

        gallery.innerHTML = '';
        data.images.forEach(item => gallery.appendChild(card(item)));

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

    const size = document.createElement('div');
    size.className = 'size';
    size.innerText = `Размер: ${item.size_kb}Кб`;

    const date = document.createElement('div');
    date.innerText = `${item.upload_date}`;

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'buttonContainer';

    const viewButton = document.createElement('button');
    viewButton.textContent = "Посмотреть";
    link.appendChild(viewButton);

    const btn = document.createElement('button');
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        handleDelete(item.id);
    });
    btn.textContent = "Удалить";

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