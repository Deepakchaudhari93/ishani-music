import base64
import httpx
import os
import config 
from config import BOT_USERNAME
from SHUKLAMUSIC import app
from pyrogram import Client, filters
import pyrogram
from uuid import uuid4
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import aiofiles, aiohttp, requests

async def image_loader(image: str, link: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 200:
                f = await aiofiles.open(image, mode="wb")
                await f.write(await resp.read())
                await f.close()
                return image
            return image

@app.on_message(filters.command("upscale", prefixes="/"))
async def upscale_image(client, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    if not replied:
        return await message.reply_text("Please Reply To An Image ...")
    if not replied.photo:
        return await message.reply_text("Please Reply To An Image ...")

    aux = await message.reply_text("Please Wait ...")
    image = await replied.download()

    try:
        # DeepAI ab sirf paid (Pro) hai — isliye photo bot ke andar hi
        # 2x badi + sharp karke di jati hai (PIL Lanczos + unsharp mask).
        from PIL import Image, ImageFilter, ImageEnhance

        out_path = f"upscaled_{uuid4().hex[:8]}.png"
        with Image.open(image) as im:
            im = im.convert("RGB")
            w, h = im.size
            im = im.resize((w * 2, h * 2), Image.LANCZOS)
            im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
            im = ImageEnhance.Contrast(im).enhance(1.05)
            im.save(out_path, "PNG")

        await aux.delete()
        await message.reply_document(out_path)
        try:
            os.remove(out_path)
            os.remove(image)
        except OSError:
            pass
    except Exception as e:
        await aux.edit_text(f"An unexpected error occurred: {str(e)}")
        

# ------------


waifu_api_url = 'https://nekos.best/api/v2/waifu'

# Ownergit
# waifu.im band ho gaya tha — ab nekos.best (free, bina key) use hota hai.

def get_waifu_data():
    response = requests.get(waifu_api_url, timeout=20)
    if response.status_code == 200:
        return response.json()
    return None

@app.on_message(filters.command("waifu"))
def waifu_command(client, message):
    try:
        waifu_data = get_waifu_data()

        if waifu_data and waifu_data.get('results'):
            image_url = waifu_data['results'][0]['url']
            message.reply_photo(image_url)
        else:
            message.reply_text("No waifu found.")

    except Exception as e:
        message.reply_text(f"An error occurred: {str(e)}")