import os
import logging
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup, LinkPreviewOptions

import config
from SHUKLAMUSIC import Carbon, YouTube, app
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.misc import db
from SHUKLAMUSIC.utils.database import add_active_video_chat, is_active_chat
from SHUKLAMUSIC.utils.exceptions import AssistantErr
from SHUKLAMUSIC.utils.inline import aq_markup, close_markup, stream_markup
from SHUKLAMUSIC.utils.pastebin import SHUKLABin
from SHUKLAMUSIC.utils.stream.queue import put_queue, put_queue_index

log = logging.getLogger("stream")
send_now_playing = None

async def get_caption(_, link, title, duration, user):
    # Defensive: _ must be the language strings dict. A caller once
    # passed a bool here (YouTube.download's 2nd return value shadowed
    # _), which killed the whole now-playing card with TypeError.
    if not isinstance(_, dict):
        from strings import get_string
        _ = get_string("en")
    return _["stream_1"].format(link, title, duration, user)

async def _announce(_, chat_id, original_chat_id, link, title, duration_min, user_name, user_id, thumb=None, classic_markup="stream", classic_text=None):
    # Rich card first (the screenshot look: big artwork, DUR_BAR row, big
    # blue pill buttons, AUTOPLAY / Go VC-LESS / CLOSE). send_now_playing
    # is injected by play.py; if it returns a message, use it. Otherwise
    # fall through to the classic photo player (live timer) below.
    # Never raise: a card failure must not kill a song that is already
    # playing (it used to surface as general_2 "TypeError" on /play).
    if send_now_playing is not None:
        try:
            run = await send_now_playing(_, original_chat_id, chat_id, link, title, duration_min, user_name, user_id, thumb)
            if run is not None:
                return run, "rich"
        except Exception as e:
            log.warning("rich now-playing failed, sending classic: %r", e)
    try:
        cap = classic_text or await get_caption(_, link, (title or "Unknown")[:70], duration_min, user_name)
        photo = thumb or config.STREAM_IMG_URL
        if photo:
            try:
                run = await app.send_photo(
                    original_chat_id,
                    photo=photo,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(stream_markup(_, chat_id, dur=duration_min)),
                )
                return run, classic_markup
            except Exception as e:
                log.warning("photo now-playing failed, sending text: %r", e)
        try:
            run = await app.send_message(
                original_chat_id, text=cap, link_preview_options=LinkPreviewOptions(is_disabled=False, show_above_text=True),
                reply_markup=InlineKeyboardMarkup(stream_markup(_, chat_id, dur=duration_min)),
            )
            return run, classic_markup
        except Exception:
            log.exception("text now-playing failed")
            return None, classic_markup
    except Exception:
        log.exception("now-playing announce failed")
        return None, classic_markup


async def stream(_, mystic, user_id, result, chat_id, user_name, original_chat_id, video: Union[bool, str] = None, streamtype: Union[bool, str] = None, spotify: Union[bool, str] = None, forceplay: Union[bool, str] = None):
    if not result: return
    if forceplay: await SHUKLA.force_stop_stream(chat_id)

    # --- PLAYLIST ---
    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT: continue
            try:
                (title, duration_min, duration_sec, thumbnail, vidid) = await YouTube.details(search, False if spotify else True)
            except: continue
            if str(duration_min) == "None" or duration_sec > config.DURATION_LIMIT: continue

            if await is_active_chat(chat_id):
                await put_queue(chat_id, original_chat_id, f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio")
                count += 1
                msg += f"{count}. {title[:70]}\n{_['play_20']} {len(db.get(chat_id)) - 1}\n\n"
            else:
                if not forceplay: db[chat_id] = []
                status = True if video else None
                try:
                    if video: _vid, file_path = await YouTube.video(f"https://www.youtube.com/watch?v={vidid}")
                    else: file_path, _direct = await YouTube.download(f"https://www.youtube.com/watch?v={vidid}", mystic)
                except: continue
                
                await SHUKLA.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail)
                await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay)

                link = f"https://t.me/{app.username}?start=info_{vidid}"
                run, mk = await _announce(_, chat_id, original_chat_id, link, title, duration_min, user_name, user_id, thumbnail, "stream")
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = mk

        if count == 0: return
        link = await SHUKLABin(msg)
        car = os.linesep.join(msg.split(os.linesep)[:17]) if msg.count("\n") >= 17 else msg
        carbon = await Carbon.generate(car, randint(100, 10000000))
        return await app.send_photo(original_chat_id, photo=carbon, caption=_["play_21"].format(len(db.get(chat_id))-1, link), reply_markup=close_markup(_))

    # --- YOUTUBE (All-in-One: API + Cookies) ---
    elif streamtype == "youtube":
        vidid, title, duration_min = result["vidid"], result["title"].title(), result["duration_min"]
        thumbnail, status = result["thumb"], True if video else None

        if await is_active_chat(chat_id):
            # Queue by video id only (vid_). change_stream re-downloads a
            # FRESH URL at play time. Storing the resolved URL here goes
            # stale while the current song plays (Ritesh media URLs
            # expire), so the next song would fail to start and the
            # assistant would sit silent in VC.
            await put_queue(chat_id, original_chat_id, f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio")
            position = len(db.get(chat_id)) - 1
            try:
                await app.send_message(original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
            except Exception:
                log.exception("queue card failed (song is queued)")
        else:
            try:
                if video:
                    n, file_path = await YouTube.video(vidid)
                else:
                    file_path, _direct = await YouTube.download(vidid, mystic)
            except Exception as e:
                raise AssistantErr(str(e))
            if not forceplay: db[chat_id] = []
            await SHUKLA.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail)
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay)

            link = f"https://t.me/{app.username}?start=info_{vidid}"
            run, mk = await _announce(_, chat_id, original_chat_id, link, title, duration_min, user_name, user_id, thumbnail, "stream")
            if run is not None:
                db[chat_id][0]["mystic"], db[chat_id][0]["markup"] = run, mk

    # --- SOUNDCLOUD ---
    elif streamtype == "soundcloud":
        file_path, title, duration_min = result["filepath"], result["title"], result["duration_min"]
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "audio")
            await app.send_message(original_chat_id, text=_["queue_4"].format(len(db.get(chat_id))-1, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay: db[chat_id] = []
            await SHUKLA.join_call(chat_id, original_chat_id, file_path, video=None)
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "audio", forceplay=forceplay)
            run, mk = await _announce(_, chat_id, original_chat_id, config.SUPPORT_CHAT, title, duration_min, user_name, user_id, None, "tg")
            db[chat_id][0]["mystic"], db[chat_id][0]["markup"] = run, mk

    # --- TELEGRAM (Direct File Play) ---
    elif streamtype == "telegram":
        file_path, link, title, duration_min = result["path"], result["link"], result["title"].title(), result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "video" if video else "audio")
            await app.send_message(original_chat_id, text=_["queue_4"].format(len(db.get(chat_id))-1, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay: db[chat_id] = []
            await SHUKLA.join_call(chat_id, original_chat_id, file_path, video=status)
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "video" if video else "audio", forceplay=forceplay)
            if video: await add_active_video_chat(chat_id)
            run, mk = await _announce(_, chat_id, original_chat_id, link, title, duration_min, user_name, user_id, None, "tg")
            db[chat_id][0]["mystic"], db[chat_id][0]["markup"] = run, mk

    # --- LIVE ---
    elif streamtype == "live":
        link, vidid, title, thumbnail = result["link"], result["vidid"], result["title"].title(), result["thumb"]
        duration_min, status = "Live Track", True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio")
            await app.send_message(original_chat_id, text=_["queue_4"].format(len(db.get(chat_id))-1, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay: db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0: raise AssistantErr(_["str_3"])
            await SHUKLA.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail if thumbnail else None)
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay)
            link = f"https://t.me/{app.username}?start=info_{vidid}"
            run, mk = await _announce(_, chat_id, original_chat_id, link, title, duration_min, user_name, user_id, thumbnail, "tg")
            db[chat_id][0]["mystic"], db[chat_id][0]["markup"] = run, mk

    # --- INDEX / M3U8 ---
    elif streamtype == "index":
        link, title, duration_min = result, "ɪɴᴅᴇx ᴏʀ ᴍ3ᴜ8 ʟɪɴᴋ", "00:00"
        if await is_active_chat(chat_id):
            await put_queue_index(chat_id, original_chat_id, "index_url", title, duration_min, user_name, link, "video" if video else "audio")
            await mystic.edit_text(text=_["queue_4"].format(len(db.get(chat_id))-1, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay: db[chat_id] = []
            await SHUKLA.join_call(chat_id, original_chat_id, link, video=True if video else None)
            await put_queue_index(chat_id, original_chat_id, "index_url", title, duration_min, user_name, link, "video" if video else "audio", forceplay=forceplay)
            run, mk = await _announce(_, chat_id, original_chat_id, link, title, duration_min, user_name, user_id, None, "tg", classic_text=_["stream_2"].format(user_name))
            db[chat_id][0]["mystic"], db[chat_id][0]["markup"] = run, mk
            await mystic.delete()