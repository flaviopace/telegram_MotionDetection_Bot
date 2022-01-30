#!/usr/bin/env python

import telegram
import json
import os
import sys
import argparse

JSON_FILE = 'config.json'
PHOTO_PATH = 'img/sample.png'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Input arguments.')
    parser.add_argument('--file', dest='fileFullPath',  default=None,
                        help='Full Image Path')
    parser.add_argument('--config', dest='configFile', default=JSON_FILE,
                        help='Full Config JASON Path')


    args = parser.parse_args()
    # load Config
    with open(os.path.join(sys.path[0], args.configFile), 'r') as in_file:
        conf = json.load(in_file)
    # Initialize Bot
    bot = telegram.Bot(token=conf['telegram_bot_config']['token_id'])
    msg = bot.send_message(chat_id=conf['telegram_bot_config']['channel_id'], text="Movimento Rilevato")
    meg = bot.send_photo(chat_id=conf['telegram_bot_config']['channel_id'], photo=open(args.fileFullPath, 'rb'))
