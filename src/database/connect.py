from dotenv import load_dotenv
import redis
from ..core.config import settings
from pymongo import MongoClient
# from sqlalchemy import create_engine

load_dotenv()


# def init_connection_engine():
#     db_config = {
#         "pool_size": 15,
#         "max_overflow": 25,
#         "pool_timeout": 86400,  # 30 seconds
#         "pool_recycle": 1800,  # 30 minutes
#         "pool_pre_ping": True,
#         "echo": True,
#     }

#     return init_tcp_connection_engine(db_config)


# def init_tcp_connection_engine(db_config):
#     pool = create_engine(settings.DATABASE_URL, **db_config)
#     return pool
# get_db = init_connection_engine()

redis_client = redis.Redis.from_url(settings.REDIS_URL)
client = MongoClient(f"{settings.KMONGO_URL}/?retryWrites=true&w=majority")
