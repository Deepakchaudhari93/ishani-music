from pyrogram import filters
from pyrogram.types import Message

from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils.database import get_autoplay, set_autoplay
from SHUKLAMUSIC.utils.decorators import AdminRightsCheck
from SHUKLAMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(
        ["autoplay", "autoplayon", "autoplayoff", "autoplayenable", "autoplaydisable"]
    )
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def autoplay_command(cli, message: Message, _, chat_id):
    cmd = message.command[0].lower()
    if cmd in ("autoplayon", "autoplayenable"):
        on = True
    elif cmd in ("autoplayoff", "autoplaydisable"):
        on = False
    elif len(message.command) == 2:
        arg = message.command[1].lower()
        if arg in ("on", "enable"):
            on = True
        elif arg in ("off", "disable"):
            on = False
        else:
            return await message.reply_text(_["autoplay_3"])
    elif len(message.command) == 1:
        on = not await get_autoplay(chat_id)
    else:
        return await message.reply_text(_["autoplay_3"])
    await set_autoplay(chat_id, on)
    key = "autoplay_1" if on else "autoplay_2"
    return await message.reply_text(
        text=_[key].format(message.from_user.mention),
        reply_markup=close_markup(_),
    )
