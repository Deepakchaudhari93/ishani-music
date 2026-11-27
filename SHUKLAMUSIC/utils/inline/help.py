import asyncio
import time
from typing import Union

from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC import app


# ---------------------------------------------------------------- colours
# Telegram ke sirf 3 button rang hain: primary (neela), success (hara),
# danger (laal). Har 3 second mein rang rotate hote hain (tick = time//3),
# bilkul play card ki tarah. Static messages (welcome/help) par rotator
# kuch der (2 min) chal kar ruk jata hai — hamesha edit karne se Telegram
# flood limit lagti hai aur bot band ho sakta hai.
_STYLE_NAMES = ["primary", "success", "danger"]
_STYLE_ENUMS = {
    "primary": ButtonStyle.PRIMARY,
    "success": ButtonStyle.SUCCESS,
    "danger": ButtonStyle.DANGER,
}


def _tick() -> int:
    return int(time.time()) // 3


def _rot_style(offset: int = 0, tick: int = None) -> str:
    if tick is None:
        tick = _tick()
    return _STYLE_NAMES[(tick + offset) % 3]


def _fancy_label(text: str) -> str:
    """String wale label ko welcome wale font mein saaf karo (˹˼ hatao)."""
    return (text or "").replace("˹", "").replace("˼", "").strip()


# ---------------------------------------------------------------- rotator
_ROTATORS = {}  # chat_id -> asyncio.Task (ek chat mein ek hi rotator)


async def _rotator_loop(msg, render, duration: int):
    """Har 3s mein render(tick) bulao; duration ke baad ruk jao.
    render False return kare ya message delete ho jaye to ruk jao."""
    start = time.time()
    try:
        while time.time() - start < duration:
            await asyncio.sleep(3)
            try:
                ok = await render(_tick())
            except FloodWait as e:
                if e.value > 15:
                    break
                await asyncio.sleep(e.value)
                continue
            except Exception:
                break
            if ok is False:
                break
    except asyncio.CancelledError:
        pass
    finally:
        _ROTATORS.pop(msg.chat.id, None)


def start_rotator(msg, render, duration: int = 1800):
    """msg ke button rang har 3s mein badlo (duration seconds tak)."""
    try:
        old = _ROTATORS.get(msg.chat.id)
        if old and not old.done():
            old.cancel()
        task = asyncio.create_task(_rotator_loop(msg, render, duration))
        _ROTATORS[msg.chat.id] = task
        return task
    except Exception:
        return None


def stop_rotator(chat_id: int):
    task = _ROTATORS.pop(chat_id, None)
    if task and not task.done():
        task.cancel()


# ---------------------------------------------------------------- panel
# 31 categories (15 music + GPT + STICKER + 14 extra tools — sabke plugin
# bot mein pehle se hain aur load hote hain).
# TIDAL style: 3 button per row, pages, neeche < •  • > navigation.
_CATS = [(f"H_B_{i}", f"help_callback hb{i}") for i in range(1, 32)]
# Kuch languages (hi/pa/ru/ta) mein naye keys nahi hain — fallback labels
_FALLBACK_LABELS = {
    "H_B_1": "ᴧᴅᴍɪɴ", "H_B_2": "ᴧᴜᴛʜ", "H_B_3": "ɢ-ᴄᴧsᴛ", "H_B_4": "ʙʟ-ᴄʜᴧᴛ",
    "H_B_5": "ʙʟ-ᴜsᴇʀs", "H_B_6": "ᴄ-ᴘʟᴧʏ", "H_B_7": "ɢ-ʙᴧɴ", "H_B_8": "ʟᴏᴏᴘ",
    "H_B_9": "ʟᴏɢ", "H_B_10": "ᴘɪɴɢ", "H_B_11": "ᴘʟᴧʏ", "H_B_12": "sʜᴜғғɪʟᴇ",
    "H_B_13": "sᴇᴇᴋ", "H_B_14": "sᴏɴɢ", "H_B_15": "sᴘᴇᴇᴅ", "H_B_16": "ɢᴘᴛ",
    "H_B_17": "sᴛɪᴄᴋᴇʀ", "H_B_18": "ᴛᴧɢ-ᴧʟʟ", "H_B_19": "ɪɴғᴏ",
    "H_B_20": "ɢʀᴏᴜᴘ", "H_B_21": "ᴇxᴛʀᴧ", "H_B_22": "ɪᴍᴧɢᴇ", "H_B_23": "ᴧᴄᴛɪᴏɴ",
    "H_B_24": "sᴇᴧʀᴄʜ", "H_B_25": "ғᴏɴᴛ", "H_B_26": "ɢᴧᴍᴇs", "H_B_27": "ʜᴧsᴛᴧɢ",
    "H_B_28": "ᴛ-ɢʀᴧᴘʜ", "H_B_29": "ɪᴍᴘᴏsᴛᴇʀ", "H_B_30": "ǫᴜᴏᴛʟʏ", "H_B_31": "ғᴜɴ",
}


def total_help_pages() -> int:
    return (len(_CATS) + _PAGE_SIZE - 1) // _PAGE_SIZE
_PAGE_SIZE = 9  # per page: 3 rows x 3


def help_rows(_, page: int = 1, tick: int = None):
    """Welcome-style rows: (text, kind, value, style) tuples.
    kind: 'url' | 'callback'. Rich aur classic dono inhi se bante hain."""
    if tick is None:
        tick = _tick()
    total_pages = (len(_CATS) + _PAGE_SIZE - 1) // _PAGE_SIZE
    page = max(1, min(page, total_pages))
    start = (page - 1) * _PAGE_SIZE
    page_cats = _CATS[start : start + _PAGE_SIZE]

    rows = [
        [
            ("Support™", "url", "https://t.me/Mee_Aarush", _rot_style(0, tick)),
            ("Updates™", "url", "https://t.me/+2TXf5vdnm1UxMWM1", _rot_style(1, tick)),
        ]
    ]
    for i in range(0, len(page_cats), 3):
        row = []
        for j, (key, cb) in enumerate(page_cats[i : i + 3]):
            label = _.get(key) if hasattr(_, "get") else None
            row.append(
                (
                    _fancy_label(label or _FALLBACK_LABELS.get(key, key)),
                    "callback",
                    cb,
                    _rot_style(i + j, tick),
                )
            )
        rows.append(row)
    rows.append(
        [
            ("< •", "callback", "help_prev", _rot_style(0, tick)),
            ("• >", "callback", "help_next", _rot_style(1, tick)),
        ]
    )
    rows.append([("EXIT", "callback", "back_to_start", _rot_style(2, tick))])
    return rows


def _classic_from_rows(rows) -> InlineKeyboardMarkup:
    kb = []
    for row in rows:
        line = []
        for text, kind, value, style in row:
            kwargs = {"url": value} if kind == "url" else {"callback_data": value}
            btn = None
            if style:
                try:
                    btn = InlineKeyboardButton(
                        text, style=_STYLE_ENUMS[style], **kwargs
                    )
                except Exception:
                    btn = None
            if btn is None:
                btn = InlineKeyboardButton(text, **kwargs)
            line.append(btn)
        if line:
            kb.append(line)
    return InlineKeyboardMarkup(kb)


def help_pannel(_, START: Union[bool, int] = None, page: int = 1):
    # Classic keyboard (rich fail ho to fallback; purane callers ke liye
    # signature waisa hi rakha hai: help_pannel(_) / help_pannel(_, True)).
    return _classic_from_rows(help_rows(_, page=page))


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="〆 ʙᴀᴄᴋ 〆",
                    callback_data="back_to_help",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text="〆 ᴄʟᴏsᴇ 〆",
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
    return buttons
