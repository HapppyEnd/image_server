const gallery = document.getElementById('gallery');

// Получаем список изображений из папки /images
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