import asyncio
import json

import aio_pika
from fastapi import UploadFile

from config import settings
from core.db_core import DatabaseCore
from schemas import Book, BrokerBook, BaseBook
from core.broker_core import rabbit_connection


async def parse(file: UploadFile) -> list[Book]:
    """
    Parse uploaded file content

    :param file:
    :return: list[Book].
    """
    result = []
    byte_content = await file.read()
    content = byte_content.decode('utf-8')
    for raw_batch in content.split('\r\n\r\n\r\n\r\n\r\n\r\n'):
        title, text = raw_batch.split('\r\n\r\n\r\n', 1)
        result.append(Book(title=title.strip(), text=text))

    return result


async def background_broker_publisher_task(books: list[Book]) -> None:
    """
    Background publisher task.

    :param books: List of books to publish.
    :return: None.
    """
    for book in books:
        await rabbit_connection.send_message(
            message=aio_pika.Message(body=BrokerBook.model_validate(book).model_dump_json().encode()),
            routing_key=settings.QUEUE_NAME
        )
        await asyncio.sleep(3)


async def background_broker_consumer_task(database: DatabaseCore) -> None:
    """
    Background consumer task.

    :param database: DatabaseCore object.
    :return: None.
    """
    # Processing callback
    async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            book = BaseBook(**json.loads(message.body))
            book.x_avg_count_in_line = book.text.count('х') / len(book.text)

            # Saving to database
            await database.insert_one(book=book)

    # Declaring queue
    queue = await rabbit_connection.channel.declare_queue(settings.QUEUE_NAME, durable=True)

    await queue.consume(process_message)
