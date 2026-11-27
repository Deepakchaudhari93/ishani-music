from typing import Union
from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils.formatters import time_to_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle

def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
             style=ButtonStyle.PRIMARY,),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER, 
                icon_custom_emoji_id=5408832111773757273,
            ),
        ]
    ]
    dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
             style=ButtonStyle.PRIMARY,)
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
             style=ButtonStyle.PRIMARY,),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER, 
                icon_custom_emoji_id=5408832111773757273,
            ),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur)
    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                 style=ButtonStyle.PRIMARY,),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER, 
                    icon_custom_emoji_id=5408832111773757273,
                ),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    # Visible text buttons (▶/⏸/⏹). The old text="" + custom-emoji-only
    # buttons rendered empty/invisible, so the queue (playlist) card looked
    # broken. Matches the player card's PRIMARY blue transport row.
    buttons = [
        [
            InlineKeyboardButton(text="▶", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏸", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏹", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [InlineKeyboardButton(text="🗑 CLOSE", callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons
