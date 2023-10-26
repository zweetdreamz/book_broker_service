from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import Book
from database.session import get_session
from schemas import BaseBook


class DatabaseCore:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_one(self, book: BaseBook) -> Book:
        """

        :param book: BaseBook model to save.
        :return: Book ORM model.
        """
        new_book = Book(**book.model_dump())
        self.session.add(new_book)
        await self.session.commit()
        return new_book

    async def read_all(self) -> list[Book]:
        """

        :return: List of [Book ORM model].
        """

        result = await self.session.execute(select(Book))
        return result.scalars().all()


#  Dependency
async def get_db_core(session=Depends(get_session)) -> AsyncGenerator[DatabaseCore, None]:
    yield DatabaseCore(session)
