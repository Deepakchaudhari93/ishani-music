import re

import requests
from bs4 import BeautifulSoup as  BSP
from SHUKLAMUSIC import app as SHUKLA
from pyrogram import filters
url = "https://all-hashtag.com/library/contents/ajax_generator.php"


def _local_hashtags(text: str) -> str:
    """Site band ho to keyword se hi hashtags banao (fallback)."""
    words = [w for w in re.split(r"\W+", text.lower()) if w]
    if not words:
        return ""
    base = "".join(words)
    tags = [base] + words
    suffixes = [
        "love", "life", "lover", "photography", "instagood", "photooftheday",
        "trending", "viral", "explore", "explorepage", "follow", "like",
        "happy", "cute", "beautiful", "amazing", "best", "top", "new",
        "style", "fashion", "nature", "travel", "music", "reels", "india",
        "instagram", "followforfollowback", "likesforlike",
    ]
    tags += [base + s for s in suffixes]
    tags += suffixes[:10]
    seen, out = set(), []
    for t in tags:
        t = re.sub(r"[^a-z0-9]", "", t)
        if t and t not in seen:
            seen.add(t)
            out.append("#" + t)
    return " ".join(out[:30])


@SHUKLA.on_message(filters.command("hastag"))
async def hastag(bot, message):
    try:
        text = message.text.split(' ',1)[1]
    except IndexError:
        return await message.reply_text("Example:\n\n/hastag python")

    content = None
    try:
        data = dict(keyword=text, filter="top")
        res = requests.post(url, data, timeout=10).text
        found = BSP(res, 'html.parser').find("div", {"class":"copy-hashtags"})
        content = found.string if found else None
    except Exception:
        content = None
    if not content:
        content = _local_hashtags(text)

    await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ  ʜᴀsᴛᴀɢ :\n<pre>{content}</pre>")
    
mod_name = "Hᴀsʜᴛᴀɢ"
help= """
Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʜᴀsʜᴛᴀɢ ɢᴇɴᴇʀᴀᴛᴏʀ ᴡʜɪᴄʜ ᴡɪʟʟ ɢɪᴠᴇ ʏᴏᴜ ᴛʜᴇ ᴛᴏᴘ 𝟹𝟶 ᴀɴᴅ ᴍᴏʀᴇ ʜᴀsʜᴛᴀɢs ʙᴀsᴇᴅ ᴏғғ ᴏғ ᴏɴᴇ ᴋᴇʏᴡᴏʀᴅ sᴇʟᴇᴄᴛɪᴏɴ.
° /hastag enter word to generate hastag.
°Exᴀᴍᴘʟᴇ:  /hastag python """
