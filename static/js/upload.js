/**
 * Handles the form submission for uploading a file.
 *
 * This script listens for the 'submit' event on the upload form,
 * prevents the default form submission,
 * and sends the selected file to the server using POST request to
 * `/upload` endpoint.
 * It then displays the server's response or an error message.
 *
 * @example
 * HTML structure:
 * <form id="uploadForm">
 *   <input type="file" id="fileInput">
 *   <button type="submit">Upload</button>
 * </form>
 * <div id="responseMessage"></div>
 *
 * After a successful upload:
 * <div id="responseMessage">
 *   <p>File uploaded successfully</p>
 *   <p>View and download:
 *     <a href="http://example.com/images/filename.jpg" target="_blank">
 *         http://example.com/images/filename.jpg
 *     </a>
 *    </p>
 * </div>
 *
 * After an error:
 * <div id="responseMessage">
 *   <p>Error: File too large.</p>
 * </div>
 *
 * @throws {Error} If the fetch request fails or the response cannot be
 * processed.
 */
document.getElementById('uploadForm')
    .addEventListener('submit', async function (event) {
        event.preventDefault();

        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        const responseMessage = document.getElementById('responseMessage');

        try {
            const response = await fetch('/upload', {
                method: 'POST', body: formData
            });
            event.target.reset()

            if (response.ok) {
                const data = await response.json();
                responseMessage.innerHTML = `
                        <p>${data.message}</p>
                        <p>Посмотреть и скачать: <a href="${
                    data.file_url}" target="_blank">${data.file_url}</a></p>
                    `;
            } else {
                const errorText = await response.text();
                responseMessage.innerHTML = `<p>Ошибка: ${errorText}</p>`;
            }
        } catch (error) {
            responseMessage.innerHTML = `<p>Ошибка: ${error.message}</p>`;
        }
    });