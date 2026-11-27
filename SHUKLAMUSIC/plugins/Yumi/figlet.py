from pyrogram import filters
import asyncio
import html
import pyfiglet
from random import choice
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.handlers import MessageHandler
from SHUKLAMUSIC import app
def figle(text):
    x = pyfiglet.FigletFont.getFonts()
    font = choice(x)
    figled = str(pyfiglet.figlet_format(text,font=font))
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ", callback_data="figlet"),InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close_reply")]])
    return figled, keyboard

@app.on_message(filters.command("figlet"))
async def echo(bot, message):
    global text
    try:
        text = message.text.split(' ',1)[1]
    except IndexError:
        return await message.reply_text("Example:\n\n`/figlet SHIVANSH PAPA `")
    kul_text, keyboard = figle(text)
    await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ :\n<pre>{html.escape(kul_text)}</pre>", reply_markup=keyboard)

@app.on_callback_query(filters.regex("figlet"))
async def figlet_handler(Client, query: CallbackQuery):
  try:
      kul_text, keyboard = figle(text)
      await query.message.edit_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ :\n<pre>{html.escape(kul_text)}</pre>", reply_markup=keyboard)
  except Exception as e :
      try:
          await query.answer(str(e)[:180], show_alert=True)
      except Exception:
          pass
__mod_name__ = "Fɪɢʟᴇᴛ" 
__help__="""
❍ /figlet*:* ᴍᴀᴋᴇs ғɪɢʟᴇᴛ ᴏғ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ
Example:\n\n`/figlet SHIVANSH PAPA `"""