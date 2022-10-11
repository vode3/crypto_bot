from pyrogram import Client
import uvloop

from config import Config

uvloop.install()

bot = Client(
    name='bot',
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root='plugins'),
)

if __name__ == '__main__':
    bot.run()
