import math
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SHUKLAMUSIC import app
import config
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC.utils.database import get_autoplay_sync
from SHUKLAMUSIC.utils.formatters import time_to_seconds


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons


def _bar(played, dur):
    # Progress-bar string for "played ▣——— dur". Never raises: unparseable
    # durations (e.g. "Live Track") fall back to the start-position bar.
    try:
        played_sec = time_to_seconds(played)
        duration_sec = time_to_seconds(dur)
        percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    except Exception:
        return "▣—————————"
    umm = math.floor(percentage)
    if umm <= 10:
        return "▣—————————"
    elif umm < 20:
        return "—▣————————"
    elif umm < 30:
        return "—▣———————"
    elif umm < 40:
        return "——▣——————"
    elif umm < 50:
        return "———▣—————"
    elif umm < 60:
        return "————▣————"
    elif umm < 70:
        return "—————▣———"
    elif umm < 80:
        return "——————▣——"
    elif umm < 95:
        return "———————▣—"
    else:
        return "————————▣"


def stream_markup_timer(_, chat_id, played, dur):
    ap_on = get_autoplay_sync(chat_id)
    bar = _bar(played, dur)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data=f"timer|{chat_id}",
            )
        ],
        [
            InlineKeyboardButton(text="▶", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏸", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏹", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(
                text="🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏɴ" if ap_on else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏғғ",
                callback_data=f"ADMIN Autoplay|{chat_id}",
                style=ButtonStyle.SUCCESS if ap_on else ButtonStyle.DANGER,
            )
        ],
        [
            InlineKeyboardButton(
                text="𝖦𝗈 ᐯᑕ-ᒪᗴՏՏ (ʀᴏᴏϻ's)",
                url='https://t.me/Ishanimusice_bot/room?startapp',
                style=ButtonStyle.SUCCESS,
            )
        ],
        [InlineKeyboardButton(text="🗑 CLOSE", callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons


def stream_markup(_, chat_id, dur=None, played="0:00"):
    # Classic now-playing buttons, same layout as the rich card (3rd
    # screenshot): [bar] [▶ ⏸ ⏹] [Autoplay] [Go VC-LESS] [CLOSE].
    # dur given -> the bar row shows from the very first card; the 7s
    # markup_timer keeps it moving live.
    ap_on = get_autoplay_sync(chat_id)
    buttons = []
    if dur:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{played} {_bar(played, dur)} {dur}",
                    callback_data=f"timer|{chat_id}",
                )
            ]
        )
    buttons += [
        [
            InlineKeyboardButton(text="▶", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏸", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏹", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(
                text="🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏɴ" if ap_on else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏғғ",
                callback_data=f"ADMIN Autoplay|{chat_id}",
                style=ButtonStyle.SUCCESS if ap_on else ButtonStyle.DANGER,
            )
        ],
        [
            InlineKeyboardButton(
                text="𝖦𝗈 ᐯᑕ-ᒪᗴՏՏ (ʀᴏᴏϻ's)",
                url='https://t.me/Ishanimusice_bot/room?startapp',
                style=ButtonStyle.SUCCESS,
            )
        ],
        [InlineKeyboardButton(text="🗑 CLOSE", callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons
