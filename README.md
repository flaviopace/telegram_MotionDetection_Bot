<h1 align="center">📷 Telegram Motion Detection Bot</h1>

<p align="center">
  <em>Turn a Raspberry Pi + webcam into a smart doorway watcher that pings your Telegram the moment something moves.</em>
</p>

<p align="center">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Raspberry%20Pi-c51a4a?logo=raspberrypi&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/python-3-3776ab?logo=python&logoColor=white">
  <img alt="Motion" src="https://img.shields.io/badge/motion-4.7-blue">
  <img alt="Telegram" src="https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white">
</p>

---

## ✨ What it does

A camera pointed at your door. When [`motion`](https://motion-project.github.io/) sees movement it records a clip, and this bot pushes the **video straight to your Telegram chat** — with optional **face filtering** so you only hear about people, not passing cars or shadows.

```
  🚪  motion detected
   │
   ▼
 motion  ──saves clip──▶  detect_and_send.py ──face?──▶ 📲  Telegram (video + snapshot)
   │                          └─ no face ─▶ 🗑️  discarded, stays quiet
   │
   └──▶ telegram_cmd_handler.py  ◀── 💬  you: /pic  /video  /stop  /start  /status
```

## 🧩 Components

| File | Role |
| --- | --- |
| [`telegram_send.py`](telegram_send.py) | Pushes a picture/video to your chat. Retries + falls back to a document so a clip **never** gets lost on a slow uplink. |
| [`detect_and_send.py`](detect_and_send.py) | Optional **face filter** (OpenCV YuNet) — only forwards clips that actually contain a face. |
| [`telegram_cmd_handler.py`](telegram_cmd_handler.py) | Two-way control: snapshot, request a clip, pause/resume detection, check status. |
| [`motion.conf`](motion.conf) | Tuned `motion` config for a single door camera. |
| `config.json` | Your bot token + chat id (git-ignored). |

## 🚀 Quick start

**1. Install dependencies**
```bash
sudo apt install motion python3-opencv
pip3 install python-telegram-bot --upgrade
```

**2. Create your bot** — talk to [@BotFather](https://t.me/BotFather), grab the token, then drop it in `config.json`:
```json
{
  "telegram_bot_config": {
    "token_id": "123456:ABC-your-bot-token",
    "channel_id": "-1001234567890"
  }
}
```

**3. (Optional) enable face filtering** — download the lightweight YuNet model next to the scripts:
```bash
wget -O face_detection_yunet_2023mar.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
```

**4. Wire it into `motion`** — in [`motion.conf`](motion.conf):
```ini
# plain: every clip
on_movie_end "/usr/bin/python3 /home/pi/bot/telegram_send.py --video %f"

# smart: only clips with a face
on_movie_end "/usr/bin/python3 /home/pi/bot/detect_and_send.py --video %f"
```

**5. Run**
```bash
motion                              # start detecting
python3 telegram_cmd_handler.py     # start the command bot
```

## 💬 Bot commands

| Command | Action |
| --- | --- |
| `/pic` | Take a snapshot now |
| `/video` | Force a clip now |
| `/stop` | Pause motion detection |
| `/start` | Resume motion detection |
| `/status` | Report detection status |

## 🔒 Security notes

- `config.json` (your token) is git-ignored — keep it that way.
- `motion.conf` exposes a web UI (`:8080`) and live stream (`:8081`). Set credentials with `webcontrol_authentication` / `stream_authentication`, and **don't commit real passwords**.
- Restrict the command bot to your own Telegram user id so strangers can't disarm your camera.

## 🛠️ Tuning

Knobs worth touching, with sensible door-cam defaults already set in [`motion.conf`](motion.conf):

| Setting | Purpose |
| --- | --- |
| `threshold` | How much must change to trigger |
| `minimum_motion_frames` | Ignore single-frame noise |
| `event_gap` | Merge one visit into one clip |
| `post_capture` | Keep recording after motion stops |
| `SCORE_THRESHOLD` (in `detect_and_send.py`) | Face-detection strictness |

---

<p align="center"><sub>Built for a Raspberry Pi Zero 2 W watching a front door. 🍓</sub></p>
