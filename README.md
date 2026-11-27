# Ishani Music Bot

A Telegram group music bot that plays songs and videos in voice chats.
Built with Python (Pyrogram + PyTgCalls), actively developed and used daily
in a public music community on Telegram.

## Features

- `/play` and `/vplay` — play audio/video in group voice chats
- Queue management, skip, pause, resume, stop, shuffle, loop
- Autoplay with related-song suggestions (no repeats)
- Playlists, slider search, inline mode
- Multi-language support (strings in `strings/langs/`)
- Rich now-playing cards with inline controls
- Extra utility commands: lyrics search, weather, calculator, QR codes,
  jokes, image tools, group management helpers and more

## Tech stack

- Python 3.11, Pyrogram (kurigram), PyTgCalls
- yt-dlp + ffmpeg for media
- MongoDB for persistence
- Optional external music APIs for fast stream resolution

## Running it

1. Copy `.env.example` to `.env` and fill in your own values
   (Telegram API ID/hash from my.telegram.org, bot token from BotFather,
   assistant session string, MongoDB URI, API keys).
2. Install dependencies: `pip install -r requirements.txt`
3. Start: `bash start` (or `python3 -m SHUKLAMUSIC`)

Never commit your real `.env`, session files or cookies — they are listed
in `.gitignore` for a reason.

## License

MIT — see [LICENSE](LICENSE).
