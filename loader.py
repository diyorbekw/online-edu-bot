from aiogram import Bot, Dispatcher

from baza.postgresql import Database
from data import config

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS
GROUP = config.GROUP_ID
CHANNEL_ID = config.CHANNEL_ID

bot = Bot(TOKEN)
db = Database()
dp = Dispatcher()