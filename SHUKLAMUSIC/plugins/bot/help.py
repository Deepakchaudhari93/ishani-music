import html
import re
from typing import Union

from pyrogram import enums, filters, types
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils import help_pannel
from SHUKLAMUSIC.utils.database import get_lang
from SHUKLAMUSIC.utils.decorators.language import LanguageStart, languageCB
from SHUKLAMUSIC.utils.inline.help import (
    help_back_markup,
    help_rows,
    private_help_panel,
    start_rotator,
    stop_rotator,
    total_help_pages,
)
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers
from SHUKLAMUSIC.utils.stuffs.buttons import BUTTONS
from SHUKLAMUSIC.utils.stuffs.helper import Helper

try:  # kurigram: rich messages (welcome card jaisa pill design)
    from pyrogram.types import InputRichMessage
except Exception:  # pragma: no cover
    InputRichMessage = None

# (chat_id, message_id) -> {"kind": "rich"|"classic", "page": int, "view": "panel"|"cat"}
_HELP_STATE = {}


def rich_buttons(rows) -> str:
    out = ""
    for row in rows:
        out += "<tg-button-row>"
        for text, kind, value, style in row:
            st = f' style="{style}"' if style else ""
            label = html.escape(text, quote=False)
            if kind == "url":
                out += f'<tg-button type="url" url="{html.escape(value)}"{st}>{label}</tg-button>'
            else:
                out += f'<tg-button type="callback_data" data="{html.escape(value)}"{st}>{label}</tg-button>'
        out += "</tg-button-row>"
    return out


def _classic_to_rich(text: str) -> str:
    """Classic Telegram HTML ko rich message ke liye safe karo."""
    text = re.sub(r"</?blockquote[^>]*>", "", text or "")
    text = re.sub(r"</?spoiler>", lambda m: "</tg-spoiler>" if m.group(0)[1] == "/" else "<tg-spoiler>", text)
    return text.replace("\r", "").replace("\n", "<br>")


def help_html(_, page: int = 1, tick: int = None) -> str:
    cap = _classic_to_rich(_["help_1"].format(SUPPORT_CHAT))
    fig = f'<figure><img src="{html.escape(START_IMG_URL)}"/></figure>' if START_IMG_URL else ""
    return f"{fig}<blockquote>{cap}</blockquote>{rich_buttons(help_rows(_, page=page, tick=tick))}"


def _cat_html(text: str) -> str:
    rows = [
        [
            ("〆 ʙᴀᴄᴋ 〆", "callback", "back_to_help", "primary"),
            ("〆 ᴄʟᴏsᴇ 〆", "callback", "close", "danger"),
        ]
    ]
    return f"<blockquote>{_classic_to_rich(text)}</blockquote>{rich_buttons(rows)}"


def _start_help_rotator(msg, _):
    key = (msg.chat.id, msg.id)

    async def render(tick):
        st = _HELP_STATE.get(key)
        if not st or st.get("view") != "panel":
            return False
        if st["kind"] == "rich":
            await msg.edit_text(
                rich_message=InputRichMessage(html=help_html(_, page=st["page"], tick=tick))
            )
        else:
            await msg.edit_reply_markup(reply_markup=help_pannel(_, page=st["page"]))
        return True

    start_rotator(msg, render, duration=1800)


async def send_help(client, chat_id, _, page: int = 1):
    """Help panel bhejo — pehle rich (welcome jaisa pill design),
    fail ho to classic photo + keyboard."""
    msg = None
    kind = "classic"
    if InputRichMessage is not None and hasattr(client, "send_rich_message"):
        try:
            msg = await client.send_rich_message(
                chat_id, InputRichMessage(html=help_html(_, page=page))
            )
            kind = "rich"
        except Exception:
            msg = None
    if msg is None:
        msg = await client.send_photo(
            chat_id,
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=help_pannel(_, page=page),
        )
        kind = "classic"
    _HELP_STATE[(chat_id, msg.id)] = {"kind": kind, "page": page, "view": "panel"}
    _start_help_rotator(msg, _)
    return msg


async def edit_help(msg, _, page: int = 1):
    """Maujooda help message ko naye page par edit karo."""
    key = (msg.chat.id, msg.id)
    st = _HELP_STATE.get(key, {"kind": "classic", "page": page, "view": "panel"})
    st["page"] = page
    st["view"] = "panel"
    _HELP_STATE[key] = st
    if st["kind"] == "rich":
        try:
            await msg.edit_text(rich_message=InputRichMessage(html=help_html(_, page=page)))
            return
        except Exception:
            st["kind"] = "classic"
    try:
        await msg.edit_text(
            _["help_1"].format(SUPPORT_CHAT), reply_markup=help_pannel(_, page=page)
        )
    except Exception:
        try:
            await msg.edit_caption(
                _["help_1"].format(SUPPORT_CHAT),
                reply_markup=help_pannel(_, page=page),
            )
        except Exception:
            pass


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        await edit_help(update.message, _, page=1)
        _start_help_rotator(update.message, _)
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        await send_help(client, update.chat.id, _, page=1)


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex(r"^help_(next|prev)$") & ~BANNED_USERS)
@languageCB
async def help_page_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    msg = CallbackQuery.message
    key = (msg.chat.id, msg.id)
    st = _HELP_STATE.get(key, {"kind": "classic", "page": 1, "view": "panel"})
    total_pages = total_help_pages()
    if CallbackQuery.data == "help_next":
        page = st["page"] % total_pages + 1
    else:
        page = (st["page"] - 2) % total_pages + 1
    await edit_help(msg, _, page=page)


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    text = getattr(helpers, f"HELP_{cb[2:]}", None) if cb.startswith("hb") else None
    if text is None:
        return
    msg = CallbackQuery.message
    key = (msg.chat.id, msg.id)
    st = _HELP_STATE.get(key, {"kind": "classic", "page": 1, "view": "panel"})
    st["view"] = "cat"
    _HELP_STATE[key] = st
    stop_rotator(msg.chat.id)
    if st["kind"] == "rich":
        try:
            await msg.edit_text(rich_message=InputRichMessage(html=_cat_html(text)))
            return
        except Exception:
            st["kind"] = "classic"
    keyboard = help_back_markup(_)
    try:
        await CallbackQuery.edit_message_text(text, reply_markup=keyboard)
    except Exception:
        pass


@app.on_callback_query(filters.regex("mbot_cb") & ~BANNED_USERS)
async def helper_cb(client, CallbackQuery):
    await CallbackQuery.edit_message_text(Helper.HELP_M, reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON))


@app.on_callback_query(filters.regex('managebot123'))
async def on_back_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_pannel(_, True)
    if cb == "settings_back_helper":
        await CallbackQuery.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard
        )

@app.on_callback_query(filters.regex('mplus'))
async def mb_plugin_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"mbot_cb")]])
    if cb == "Okieeeeee":
        await CallbackQuery.edit_message_text(f"`something errors`",reply_markup=keyboard,parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await CallbackQuery.edit_message_text(getattr(Helper, cb), reply_markup=keyboard)

@app.on_callback_query(filters.regex("back_to_help") & ~BANNED_USERS)
@languageCB
async def back_to_help_panel(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    msg = CallbackQuery.message
    key = (msg.chat.id, msg.id)
    st = _HELP_STATE.get(key, {"kind": "classic", "page": 1, "view": "panel"})
    await edit_help(msg, _, page=st.get("page", 1))
    _start_help_rotator(msg, _)


@app.on_callback_query(filters.regex("help_refresh") & ~BANNED_USERS)
@languageCB
async def help_refresh_panel(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    msg = CallbackQuery.message
    key = (msg.chat.id, msg.id)
    st = _HELP_STATE.get(key, {"kind": "classic", "page": 1, "view": "panel"})
    await edit_help(msg, _, page=st.get("page", 1))
