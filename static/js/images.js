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

fetch('/api/images')
    .then(async response => {
        return await response.json()
    })
    .then(data => {
        gallery.innerHTML = '';  // Clear previous content
        console.log(data)
        data.images.map(item => {
            const link = document.createElement('a');
            link.href = `/images/${item.filename}`;
            const img = document.createElement('img');
            img.src = `/images/${item.filename}`;
            img.alt = item.filename;
            link.appendChild(img);
            gallery.appendChild(link);
        });
    })
    .catch(error => console.error('Error loading images:', error));