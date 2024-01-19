import json
import logging
import os
import traceback

import pika

# opens a new connection every time to broadcast a message, need to fix this later
rabbit_host = os.getenv("NLM_MQ_HOST", "localhost")
rabbit_username = os.getenv("NLM_MQ_USERNAME", "")
rabbit_password = os.getenv("NLM_MQ_PASSWORD", "")
if rabbit_username and rabbit_password:
    credentials = pika.PlainCredentials(rabbit_username, rabbit_password)
    parameters = pika.ConnectionParameters(
        rabbit_host,
        5672,
        "nlm",
        credentials,
    )
else:
    parameters = pika.ConnectionParameters(
        host=rabbit_host,
        port=5672,
    )

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send(task, queue_name="task_queue"):
    try:
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(task),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )
        connection.close()
        return True
    except Exception as e:
        logger.error(
            f"error in sending task {task} to queue err: {str(e)}, stacktrace: {traceback.format_exc()}",
            exc_info=True,
        )
        return False
