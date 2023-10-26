import traceback

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, BackgroundTasks, Depends, Response

from config import settings
from database.init_db import init_models
from core.book_core import parse, background_broker_publisher_task, background_broker_consumer_task
from core.db_core import get_db_core, DatabaseCore
from schemas import DefaultResponse, ReadBook
from core.broker_core import rabbit_connection


def create_app():
    def broker_consumer(background_tasks: BackgroundTasks, database: DatabaseCore = Depends(get_db_core)):
        background_tasks.add_task(background_broker_consumer_task, database)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await init_models()
        await rabbit_connection.connect()
        await rabbit_connection.channel.declare_queue(name=settings.QUEUE_NAME, durable=True)
        yield
        await rabbit_connection.disconnect()

    app = FastAPI(docs_url='/', lifespan=lifespan, dependencies=[Depends(broker_consumer)])

    @app.post(
        '/api/start_task',
        response_model=DefaultResponse,
        status_code=200,
        response_model_exclude_unset=True
    )
    async def start_broker_background_task(
            file: UploadFile,
            background_tasks: BackgroundTasks,
            response: Response
    ):
        try:
            parsed_books = await parse(file=file)
            background_tasks.add_task(background_broker_publisher_task, parsed_books)
            return DefaultResponse(success=True)
        except:
            response.status_code = 500
            return DefaultResponse(success=False, error=traceback.format_exc())

    @app.get(
        '/api/book/list',
        response_model=list[ReadBook] | DefaultResponse,
        status_code=200,
        response_model_exclude_unset=True
    )
    async def read_books(
            response: Response,
            database: DatabaseCore = Depends(get_db_core)
    ):
        try:
            return await database.read_all()
        except:
            response.status_code = 500
            return DefaultResponse(success=False, error=traceback.format_exc())

    return app


def main():
    uvicorn.run(
        f"{__name__}:create_app",
        host='0.0.0.0',
        port=8888
    )


if __name__ == '__main__':
    main()
