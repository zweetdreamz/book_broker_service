from config import settings

from dataclasses import dataclass
from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel


@dataclass
class RabbitConnection:
    connection: AbstractRobustConnection | None = None
    channel: AbstractRobustChannel | None = None

    async def _clear(self) -> None:
        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()

        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        """
        Establish connection with the RabbitMQ.

        :return: None.
        """
        self.connection = await connect_robust(settings.RABBIT_URI)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

    async def disconnect(self) -> None:
        """
        Disconnect and clear connections from RabbitMQ.

        :return: None.
        """
        await self._clear()

    async def send_message(self, message: Message, routing_key: str = settings.QUEUE_NAME) -> None:
        """
            Public message or messages to the RabbitMQ queue.

            :param message: aio_pika.Message object.
            :param routing_key: Routing key of RabbitMQ, not required. Tip: the same as in the consumer.
        """
        await self.channel.default_exchange.publish(message, routing_key=routing_key)


rabbit_connection = RabbitConnection()
