import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str("5152978553:AAGU-gfPGZ9_fbvHmkGE2F1mvkRnDXb1Ab4")
admins = [
    936590877
]

ip = os.getenv("ip")

aiogram_redis = {
    'host': ip,
}

redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}
