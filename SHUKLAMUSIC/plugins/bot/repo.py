from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SHUKLAMUSIC import app
from config import BOT_USERNAME
from SHUKLAMUSIC.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """
Jᴀᴀ ʜᴀɪ ᴘᴀᴅʜᴀɪ ᴋʀ Jᴀᴀᴋᴇ ᴀᴀʏᴀ ʙᴀᴅᴀ ʀᴇᴘᴏ ᴅᴇᴋʜɴᴇ ᴡᴀʟᴀ !
<pre>||➥ᴜᴘᴛɪᴍᴇ: 𝟷ʜ:𝟹𝟺ᴍ:𝟻𝟺s
➥sᴇʀᴠᴇʀ sᴛᴏʀᴀɢᴇ: 𝟸𝟽.𝟺%
➥ᴄᴘᴜ ʟᴏᴀᴅ: 𝟷𝟷.𝟸%
➥ʀᴀᴍ ᴄᴏɴsᴜᴍᴘᴛɪᴏɴ: 𝟷𝟽.𝟻%||</pre>
•──────────────────•
ᴘᴏᴡєʀєᴅ ʙʏ»|| [- 𝙸𝚜𝚑𝚊𝚗𝚒 𝙼𝚞𝚜𝚒𝚌 ⌯](https://t.me/Ishanimusice_bot)||
•──────────────────•
"""

@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [
            InlineKeyboardButton(text=" ˹ηєᴛᴡᴏʀᴋ˼ ", url="https://t.me/+2TXf5vdnm1UxMWM1",),
            InlineKeyboardButton(text=" ˹ϻʏ ʜᴏϻє˼ ", url="https://t.me/Mee_Aarush",),
        ],
        
     [
            InlineKeyboardButton("˹ᴘʀιᴠᴧᴄʏ˼", url=f"https://telegra.ph/Privacy-Policy-08-03-101"),
            InlineKeyboardButton("˹ɪsʜᴀɴɪ ᴛᴜηєs˼♪", url=f"https://t.me/Ishanimusice_bot/room?startapp"),
        ],
        
          [
            InlineKeyboardButton("˹ ϻʏ ϻᴧsᴛєʀ ˼ 👑", url="https://t.me/Mee_Aarush"),
          ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://ishani-music.ashubhai8935.workers.dev/img/start.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
