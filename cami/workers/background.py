import dramatiq
import requests
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from cami.utils.logger import  logger

broker = RabbitmqBroker(
    host="localhost",
    port=5672,
    middleware=[dramatiq.middleware.AsyncIO()]
)
dramatiq.set_broker(broker)


@dramatiq.actor
async def count_words(url: str) -> str:
    logger.info(f"Counting words in {url}")
    response = requests.get(url)
    count = len(response.text.split(" "))
    return f"{count} words"
