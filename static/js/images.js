/**
 * Fetches and displays a gallery of images from the server.
 *
 * This script fetches the list of images from the `/api/images`
 * endpoint, * creates HTML elements for each image, and appends them
 * to the gallery container.
 *
 * @example
 * HTML structure:
 * <div id="gallery"></div>
 *
 * After execution:
 * <div id="gallery">
 *   <a href="/images/image1.jpg">
 *      <img src="/images/image1.jpg" alt="image1">
 *   </a>
 *   <a href="/images/image2.jpg">
 *       <img src="/images/image2.jpg" alt="image2">
 *   </a>
 * </div>
 *
 * @throws {Error} If the fetch request fails or the response cannot
 * be parsed as JSON.
 */
const gallery = document.getElementById('gallery');
const deleteButton = document.getElementById('deleteButton');

const handleDelete = (id) => {
    fetch(`/api/images/${id}`, {
        method: 'DELETE'
    }).then(() => alert("Delete"))
}

fetch('/api/images')
    .then(async response => {
        return await response.json()
    })
    .then(data => {
        gallery.innerHTML = '';  // Clear previous content
        console.log(data)
        data.images.map(item => {
            // const link = document.createElement('a');
            // link.href = `/images/${item.filename}`;
            // const img = document.createElement('img');
            // img.src = `/images/${item.filename}`;
            // img.alt = item.filename;
            // link.appendChild(img);
            // gallery.appendChild(link);
            // const btn = document.createElement('button')
            // btn.addEventListener('click', () => handleDelete(item.id))
            gallery.appendChild(card(item));
        });
    })
    .catch(error => console.error('Error loading images:', error));

const card = (item) => {
    const card = document.createElement('div')
    card.className = 'card'

    const link = document.createElement('a');
    link.href = `/images/${item.filename}`;


    const imgContainer = document.createElement('div')
    imgContainer.className = 'imgContainer'

    const img = document.createElement('img');
    img.src = `/images/${item.filename}`;
    img.alt = item.filename;
    img.className = 'img'

    const textContainer = document.createElement('div')
    textContainer.className = 'textContainer'

    const titleContainer = document.createElement('div')
    titleContainer.className = 'titleContainer'

    const size = document.createElement('div')
    size.className = 'size'
    size.innerText = `Размер: ${item.size_kb}Кб`

    const date = document.createElement('div')
    date.innerText = `${item.upload_date}`

    const buttonContainer = document.createElement('div')
    buttonContainer.className = 'buttonContainer'

    const viewButton = document.createElement('button')
    viewButton.textContent = "Посмотреть"
    link.appendChild(viewButton)

    const btn = document.createElement('button')
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        handleDelete(item.id)
    })
    btn.textContent = "Удалить"

    textContainer.appendChild(size)
    textContainer.appendChild(date)
    buttonContainer.appendChild(link)
    buttonContainer.appendChild(btn)

    card.appendChild(imgContainer)
    card.appendChild(textContainer)
    card.appendChild(buttonContainer)
    imgContainer.appendChild(img)


    return card
}