#!/usr/bin/env python

"""
Simple Bot to send timed Telegram messages.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import argparse
import os
import sys
import json
import logging
import requests
import re

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

JSON_FILE = 'config.json'
ch_id = ''

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def webcontrol(type, cmd):
    req = 'http://192.168.2.100:8080/0/'+type+'/'+cmd
    resp = requests.get(req)
    if(re.search(r'b>(.*)', resp.text)):
        return re.findall(r'b>(.*)', resp.text)[0]
    elif (re.search(r'snap|make(.*)', resp.text)):
        return 'command executed!'
    else:
        return 'Invalid Request'

def help(update: Update, context: CallbackContext) -> None:
    """Sends a message."""
    update.message.reply_text('/pic or /video or /status or /stop or /start')

def snapshot(update: Update, context: CallbackContext) -> None:
    """Send the alarm message."""
    update.message.reply_text('Sending Picture to dedicated chat!')
    res = webcontrol('action', 'snapshot')
    update.message.reply_text(res)
    context.bot.send_message(chat_id=ch_id, text=res)

def video(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    update.message.reply_text('Sending Video to dedicated chat!')
    res = webcontrol('action', 'makemovie')
    update.message.reply_text(res)
    context.bot.send_message(chat_id=ch_id, text=res)

def pause(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    update.message.reply_text('Pause Motion Detection!')
    res = webcontrol('detection', 'pause')
    update.message.reply_text(res)
    context.bot.send_message(chat_id=ch_id, text=res)

def start(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    update.message.reply_text('Start Motion Detection!')
    res = webcontrol('detection', 'start')
    update.message.reply_text(res)
    context.bot.send_message(chat_id=ch_id, text=res)

def status(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    update.message.reply_text('Status Motion:')
    res = webcontrol('detection', 'status')
    update.message.reply_text(res)
    context.bot.send_message(chat_id=ch_id, text=res)

def status1(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    job = context.job
    global ch_id
    context.bot.send_message(chat_id=update.message.chat_id, text='Send Status Info to dedicated chat!')
    context.bot.send_message(chat_id=ch_id, text='Send Status Info to dedicated chat!')

def main() -> None:
    parser = argparse.ArgumentParser(description='Process Input arguments.')
    parser.add_argument('--config', dest='configFile', default=JSON_FILE,
                        help='Full Config JASON Path')

    args = parser.parse_args()
    # load Config
    with open(os.path.join(sys.path[0], args.configFile), 'r') as in_file:
        conf = json.load(in_file)
    global ch_id
    ch_id = conf['telegram_bot_config']['channel_id']
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(conf['telegram_bot_config']['token_id'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help))
    #pic
    dispatcher.add_handler(CommandHandler("pic", snapshot))
    #video
    dispatcher.add_handler(CommandHandler("video", video))
    #motion
    dispatcher.add_handler(CommandHandler("stop", pause))
    dispatcher.add_handler(CommandHandler("start", start))
    #help
    dispatcher.add_handler(CommandHandler("status", status))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()