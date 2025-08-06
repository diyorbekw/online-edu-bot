from dotenv import load_dotenv
from environs import Env

load_dotenv()

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  
ADMINS = list(map(int,env.list("ADMINS")))  
CHANNELS = list(map(int,env.list("CHANNELS"))) 
GROUP_ID = env.str("GROUP_ID")
CHANNEL_ID = env.str("CHANNEL_ID")