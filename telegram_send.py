#!/usr/bin/python3

import telegram
import json
import os
import sys
import time
import argparse

JSON_FILE = 'config.json'
PHOTO_PATH = 'img/sample.png'
CAPTION = "Movimento Rilevato"

# Slow upstream on a Pi Zero 2 W: give uploads room and retry on failure so a
# big clip doesn't leave you with just the text message.
UPLOAD_TIMEOUT = 120     # seconds
RETRIES = 3
RETRY_DELAY = 5          # seconds between attempts


def send_with_retry(send_fn):
    """Call send_fn() up to RETRIES times; raise the last error if all fail."""
    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            return send_fn()
        except Exception as err:          # network/timeout/Telegram errors
            last_err = err
            print("send attempt {}/{} failed: {}".format(attempt, RETRIES, err),
                  file=sys.stderr)
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY)
    raise last_err


def force_send_video(bot, chat, path):
    """Get the clip through no matter what: try as an inline video, and if that
    keeps failing fall back to sending it as a plain document (more lenient on
    format/size, so it almost always delivers)."""
    try:
        with open(path, 'rb') as video:
            return send_with_retry(lambda: bot.send_video(
                chat_id=chat, video=video, caption=CAPTION,
                timeout=UPLOAD_TIMEOUT))
    except Exception as err:
        print("send_video failed, falling back to document: {}".format(err),
              file=sys.stderr)
        with open(path, 'rb') as doc:
            return send_with_retry(lambda: bot.send_document(
                chat_id=chat, document=doc, caption=CAPTION,
                timeout=UPLOAD_TIMEOUT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Input arguments.')
    parser.add_argument('--pic', dest='fileFullPath', default=None,
                        help='Full Image Path')
    parser.add_argument('--video', dest='videoFullPath', default=None,
                        help='Full Video Path')
    parser.add_argument('--config', dest='configFile', default=JSON_FILE,
                        help='Full Config JSON Path')

    args = parser.parse_args()
    # load Config
    with open(os.path.join(sys.path[0], args.configFile), 'r') as in_file:
        conf = json.load(in_file)

    # Initialize Bot
    bot = telegram.Bot(token=conf['telegram_bot_config']['token_id'])
    chat = conf['telegram_bot_config']['channel_id']

    # Send the caption *with* the media so you never get an orphan text message
    # without its picture/video. Only send a standalone text when there's no file.
    if args.videoFullPath:
        force_send_video(bot, chat, args.videoFullPath)
    elif args.fileFullPath:
        with open(args.fileFullPath, 'rb') as photo:
            send_with_retry(lambda: bot.send_photo(
                chat_id=chat, photo=photo, caption=CAPTION,
                timeout=UPLOAD_TIMEOUT))
    else:
        send_with_retry(lambda: bot.send_message(chat_id=chat, text=CAPTION))
