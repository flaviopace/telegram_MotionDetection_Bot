import telegram
import time
import json
import os
import sys

JSON_FILE = 'config.json'

PHOTO_PATH = 'img/sample.png'

if __name__ == "__main__":
    # load Config
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
    # Initialize Bot
    bot = telegram.Bot(token=conf['telegram_bot_config']['token_id'])
    bot.send_message(chat_id=conf['telegram_bot_config']['channel_id'], text="Movimento Rilevato")
    bot.send_photo(chat_id=conf['telegram_bot_config']['channel_id'], photo=open(PHOTO_PATH, 'rb'))
