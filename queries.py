"""Module containing all SQL queries for the application."""

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    size INTEGER NOT NULL,
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_type VARCHAR(10) NOT NULL
)
"""

INSERT_IMAGE = """
INSERT INTO images 
(filename, original_name, size, file_type) 
VALUES (%s, %s, %s, %s)
RETURNING id
"""

GET_IMAGES = """
SELECT 
    id,
    filename,
    original_name,
    size,
    upload_time,
    file_type,
    size/1024 AS size_kb,
    to_char(upload_time, 'YYYY-MM-DD HH24:MI:SS') AS upload_date
FROM images
ORDER BY upload_time DESC
LIMIT %s OFFSET %s
"""

COUNT_IMAGES = "SELECT COUNT(*) FROM images"

FIND_IMAGE = "SELECT filename FROM images WHERE filename = %s"

DELETE_IMAGE = "DELETE FROM images WHERE filename = %s"