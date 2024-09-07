"""Orchestrator for the tasks in the products app."""

import os
import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker

# init dramatiq broker
broker = RedisBroker(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("DRAMATIQ_REDIS_DB", 0)),
    namespace=os.getenv("DRAMATIQ_NAME_SPACE", "product-management-dramatiq"),
)
dramatiq.set_broker(broker)

redis_conn = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), db=int(os.getenv("REDIS_DB", 1)))
