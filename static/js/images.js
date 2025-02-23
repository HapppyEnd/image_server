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
    .then(response => response.json())
    .then(data => {
        data.images.map(name => {
            const link = document.createElement('a');
            link.href = `/images/${name}`;
            const img = document.createElement('img');
            img.src = `/images/${name}`;
            img.alt = name;
            link.appendChild(img);
            gallery.appendChild(link);
        });
    })
    .catch(error => console.error('Error loading images:', error));