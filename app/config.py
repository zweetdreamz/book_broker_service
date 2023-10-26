from dotenv import load_dotenv
import os

from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    RABBIT_URI = os.environ.get('RABBIT_URI')
    QUEUE_NAME = os.environ.get('QUEUE_NAME')

    DATABASE_URI = os.environ.get('DATABASE_URI')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')

    API_PREFIX = '/api'

    DB_NAME = 'postgres'


settings = Settings()
