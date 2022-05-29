import asyncio
from kafka import KafkaConsumer, KafkaProducer
import logging
import os
import json
from rediscluster import RedisCluster
import time

from AI.dialogue import init_new_dialogue

consumer = KafkaConsumer(os.getenv("ID_HOST"), bootstrap_servers=os.getenv("KAFKA_HOST", ""))
producer = KafkaProducer(bootstrap_servers=os.getenv("KAFKA_HOST", ""), retries=5)

redis_connect = json.loads(os.getenv('REDIS_CONNECT', ''))
startup_nodes = redis_connect.get('hosts')
password = redis_connect.get('password')
redis_db = RedisCluster(startup_nodes=startup_nodes, password=password, decode_responses=True)


async def handler_message(user_id):
    conversation, nlp = await init_new_dialogue(user_id)            # получение объектов для генерации ответа от ИИ
    result = nlp([conversation], do_sample=False, max_length=1000)  # обработка нейронной сетью (ИИ)
    text_to_user = list(result.iter_texts())[-1][1]

    data = ['bot', text_to_user, f'time#{int(time.time())}']
    redis_db.rpush(user_id, *data)  # запись ответного сообщения пользователю в redis

    # положить в kafka-канал
    producer.send('answer_ch', key=user_id.encode("utf-8"), value=text_to_user.encode("utf-8"))


async def handler_kafka_event():
    for message in consumer:    # обработка всех новых сообщений из kafka
        user_id = message.key.decode("utf-8")
        text_message = message.value.decode("utf-8")

        data = ['user', text_message, f'time#{int(time.time())}']
        redis_db.rpush(user_id, *data)  # запись сообщения от пользователя в redis

        await handler_message(user_id=user_id)  # отправить на обработку в функцию взаимодействия с ИИ


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handler_kafka_event())
