import dramatiq
import requests
from dramatiq.brokers.rabbitmq import RabbitmqBroker

broker = RabbitmqBroker(
    host="localhost",
    port=5672,
    middleware=[dramatiq.middleware.AsyncIO()]
)
dramatiq.set_broker(broker)


@dramatiq.actor
async def count_words(url: str) -> str:
    response = requests.get(url)
    count = len(response.text.split(" "))
    return f"{count} words"
