document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const responseMessage = document.getElementById('responseMessage');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            responseMessage.innerHTML = `
                        <p>${data.message}</p>
                        <p>File URL: <a href="${data.file_url}" target="_blank">${data.file_url}</a></p>
                    `;
        } else {
            const errorText = await response.text();
            responseMessage.innerHTML = `<p>Error: ${errorText}</p>`;
        }
    } catch (error) {
        responseMessage.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});