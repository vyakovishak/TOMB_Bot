import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str("API_KEY")
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
