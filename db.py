import os
from typing import Any, Optional

import psycopg
from loguru import logger
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
import constants
from constants import ITEMS_PER_PAGE
from queries import (
    CREATE_TABLE,
    INSERT_IMAGE,
    GET_IMAGES,
    COUNT_IMAGES,
    FIND_BY_ID,
    DELETE_BY_ID
)

log_file = os.path.join('logs', constants.LOG_FILE)
logger.add(log_file, format=constants.LOG_FORMAT, level=constants.LOG_LEVEL)


class Database:
    """Singleton class for managing database connections"""
    _instance = None
    _initialized = False

    def __new__(cls):
        """Create or return singleton instance.

        Returns:
            Database: Singleton database instance.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the database instance."""
        if not self._initialized:
            self.pool: Optional[AsyncConnectionPool] = None
            self._initialized: bool = True

    async def connect(self, dsn: str = constants.DATABASE_URL) -> None:
        """Initialize the connection pool.

        Args:
            dsn: Database connection string. Defaults from constants.
        Raises:
            ConnectionError: If connection to database fails.
        """
        if self.pool is not None:
            return
        try:
            self.pool = AsyncConnectionPool(
                conninfo=dsn,
                min_size=constants.DB_POOL_MIN_SIZE,
                max_size=constants.DB_POOL_MAX_SIZE,
                open=False
            )
            await self.pool.open()
            await self.pool.wait()
            logger.success(constants.DB_POOL_SUCCESS)
        except psycopg.OperationalError as e:
            logger.error(constants.ERROR_DB_CONNECTION)
            raise ConnectionError(constants.ERROR_DB_CONNECTION) from e

    async def disconnect(self) -> None:
        """Close all connections in the pool.

        Raises:
            ConnectionError: If disconnection fails.
        """
        if self.pool is None:
            return
        try:
            await self.pool.close()
            self.pool = None
            logger.success(constants.DB_POOL_CLOSE_SUCCESS)
        except psycopg.OperationalError as e:
            logger.error(constants.DISCONNECT_FAILED)
            raise ConnectionError(constants.DISCONNECT_FAILED) from e

    async def init_db(self) -> None:
        """Initialize database tables.

        Raises:
            RuntimeError: If database connection is not established.
            RuntimeError: If table creation fails.
        """
        if self.pool is None:
            raise RuntimeError(constants.DB_CONNECTION_NOT_ESTABLISH)

        try:
            async with self.pool.connection() as conn:
                await conn.execute(CREATE_TABLE)
                logger.success(constants.CREATE_TABLE_SUCCESS)
        except psycopg.Error as e:
            logger.error(f'{constants.CREATE_TABLE_ERROR}: {e}')
            raise RuntimeError(constants.CREATE_TABLE_ERROR) from e

    async def insert_image(
            self,
            filename: str,
            original_name: str,
            size: int,
            file_type: str
    ) -> int:
        """Insert image metadata into database.

        Args:
            filename: Generated unique filename.
            original_name: Original filename from user.
            size: File size in bytes.
            file_type: File extension/type.
        Returns:
            int: The ID of the inserted image record.
        Raises:
            RuntimeError: If database connection is not established.
            RuntimeError: If image insertion fails.
        """
        if self.pool is None:
            raise RuntimeError(constants.DB_CONNECTION_NOT_ESTABLISH)

        try:
            async with self.pool.connection() as conn:
                result = await conn.execute(
                    INSERT_IMAGE,
                    (filename, original_name, size, file_type)
                )
                row = await result.fetchone()
                image_id = row[0]
                logger.info(
                    constants.IMG_INSERT_SUCCESS.format(image_id=image_id))
                return image_id
        except psycopg.Error as e:
            logger.error(constants.IMG_INSERT_FAILED.format(error=e))
            raise RuntimeError(constants.IMG_INSERT_FAILED) from e

    async def get_images(
            self,
            page: int = 1,
    ) -> dict[str, Any]:
        """Get paginated list of images from database.

        Args:
            page: Page number to retrieve (1-based).

        Returns:
            dict: Dictionary containing:
                - images: List of image records
                - total: Total number of images
                - page: Current page number
                - per_page: Items per page
                - total_pages: Total number of pages

        Raises:
            RuntimeError: If database connection is not established.
            RuntimeError: If image retrieval fails.
        """
        if self.pool is None:
            raise RuntimeError(constants.DB_CONNECTION_NOT_ESTABLISH)

        offset: int = (page - 1) * ITEMS_PER_PAGE
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as images_cur:
                    await images_cur.execute(GET_IMAGES,
                                             (ITEMS_PER_PAGE, offset))
                    columns = [desc[0] for desc in images_cur.description]
                    images = [dict(zip(columns, row)) for row in
                              await images_cur.fetchall()]

                async with conn.cursor() as count_cur:
                    await count_cur.execute(COUNT_IMAGES)
                    result = await count_cur.fetchone()
                    total = result[0] if result else 0

                return {
                    'images': images,
                    'total': total,
                    'page': page,
                    'per_page': ITEMS_PER_PAGE,
                    'total_pages': (total + ITEMS_PER_PAGE - 1
                                    ) // ITEMS_PER_PAGE
                }
        except psycopg.Error as e:
            logger.error(constants.FAIL_TO_FETCH_IMG.format(error=e))
            raise RuntimeError(constants.FAIL_TO_FETCH_IMG) from e

    async def delete_image(self, image_id: str) -> tuple[bool, Optional[str]]:
        """Delete an image record from database.

        Args:
            image_id: ID of the image to delete.
        Returns:
            bool: True if success, False if image not found.
        Raises:
            RuntimeError: If database connection is not established.
            RuntimeError: If image deletion fails.
        """
        if self.pool is None:
            raise RuntimeError(constants.DB_CONNECTION_NOT_ESTABLISH)

        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        FIND_BY_ID,
                        (image_id,)
                    )
                    filename = await cur.fetchone()
                    if not filename:
                        logger.warning(constants.FILE_NOT_FOUND)
                        return False, None

                    await cur.execute(
                        DELETE_BY_ID,
                        (image_id,)
                    )
                    await cur.fetchone()
                    logger.info(
                        constants.IMG_DELETE_SUCCESS.format(filename=filename))
                    return True, filename
        except psycopg.Error as e:
            logger.error(constants.IMG_DELETE_FAILED.format(error=e))
            raise RuntimeError(constants.IMG_DELETE_FAILED) from e
