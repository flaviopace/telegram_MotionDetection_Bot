#!/usr/bin/python3

"""
Post-filter for motion clips: detect human faces in a captured video and only
forward it to Telegram when at least one face is found. Clips with no face are
deleted so you stop getting notified about cars, shadows and pets.

Wire it from motion.conf instead of telegram_send.py:
    on_movie_end "/usr/bin/python3 /home/pi/bot/detect_and_send.py --video %f"

Requires OpenCV (>=4.5.4 for FaceDetectorYN) and the YuNet model:
    sudo apt install python3-opencv      # or: pip3 install opencv-python
    wget -O face_detection_yunet_2023mar.onnx \
      https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
"""

import argparse
import json
import os
import sys

import cv2
import telegram

JSON_FILE = 'config.json'
# YuNet model, kept next to this script.
MODEL = os.path.join(sys.path[0], 'face_detection_yunet_2023mar.onnx')

# Analyse at most this many frames spread across the clip. Kept low because the
# Pi Zero 2 W (512 MB, no GPU) decodes/detects in software.
SAMPLE_FRAMES = 8
# Run detection on a downscaled copy this wide, then map boxes back to full res.
# Much faster/lighter on the Zero 2 W with little accuracy loss for door-sized faces.
DETECT_WIDTH = 320
# Minimum YuNet confidence to count as a face (0..1). Raise to cut false hits.
SCORE_THRESHOLD = 0.8


def best_face_frame(video_path):
    """Return (annotated_frame, score) for the highest-confidence face in the
    clip, or (None, 0.0) if no face passes SCORE_THRESHOLD."""
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    step = max(total // SAMPLE_FRAMES, 1)

    detector = cv2.FaceDetectorYN.create(MODEL, "", (DETECT_WIDTH, DETECT_WIDTH),
                                         SCORE_THRESHOLD)

    best_frame, best_score = None, 0.0
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            h, w = frame.shape[:2]
            scale = DETECT_WIDTH / float(w)
            small = cv2.resize(frame, (DETECT_WIDTH, int(h * scale)))
            detector.setInputSize((small.shape[1], small.shape[0]))
            _, faces = detector.detect(small)
            if faces is not None:
                for f in faces:
                    score = float(f[-1])
                    if score > best_score:
                        # Map the box from the downscaled image back to full res.
                        x, y, bw, bh = (int(v / scale) for v in f[:4])
                        annotated = frame.copy()
                        cv2.rectangle(annotated, (x, y), (x + bw, y + bh),
                                      (0, 255, 0), 2)
                        best_frame, best_score = annotated, score
        idx += 1
    cap.release()
    return best_frame, best_score


def main():
    parser = argparse.ArgumentParser(description='Face-filter a motion clip.')
    parser.add_argument('--video', dest='videoFullPath', required=True,
                        help='Full path to the captured movie')
    parser.add_argument('--config', dest='configFile', default=JSON_FILE,
                        help='Full Config JSON Path')
    args = parser.parse_args()

    with open(os.path.join(sys.path[0], args.configFile), 'r') as in_file:
        conf = json.load(in_file)

    frame, score = best_face_frame(args.videoFullPath)
    if frame is None:
        # No face -> discard the clip and stay silent.
        try:
            os.remove(args.videoFullPath)
        except OSError:
            pass
        return

    snap = args.videoFullPath + '.face.jpg'
    cv2.imwrite(snap, frame)

    bot = telegram.Bot(token=conf['telegram_bot_config']['token_id'])
    chat = conf['telegram_bot_config']['channel_id']
    bot.send_message(chat_id=chat, text="Volto rilevato ({:.0%})".format(score))
    with open(snap, 'rb') as photo:
        bot.send_photo(chat_id=chat, photo=photo)
    with open(args.videoFullPath, 'rb') as video:
        bot.send_video(chat_id=chat, video=video)
    os.remove(snap)


if __name__ == "__main__":
    main()
