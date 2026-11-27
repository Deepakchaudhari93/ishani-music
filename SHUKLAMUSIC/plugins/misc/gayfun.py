from pyrogram.types import Message
import random
from pyrogram import Client, filters, idle
import pyrogram, asyncio, random, time
from pyrogram.errors import FloodWait
from pyrogram.types import *
import requests
from SHUKLAMUSIC import app

def calculate_gay_percentage():
    # Simple random gay percentage calculation for fun
    return random.randint(1, 100)


def generate_gay_response(gay_percentage):
    # Define random texts and emojis for different gay percentage ranges
    if gay_percentage < 30:
        return "You're straight as an arrow. 🏳️‍🌈"
    elif 30 <= gay_percentage < 70:
        return "You might have a bit of a rainbow in you. 🌈"
    else:
        return "You're shining with rainbow colors! 🌟🏳️‍🌈"

@app.on_message(filters.command("gay") & filters.regex(r'^/gay$'))
def gay_calculator_command(client, message: Message):
    # Calculate gay percentage
    gay_percentage = calculate_gay_percentage()

    # Generate gay response
    gay_response = generate_gay_response(gay_percentage)

    # Send the gay response as a message
    message.reply_text(f"Gay Percentage: {gay_percentage}%\n{gay_response}")




from urllib.parse import quote
import io
import aiohttp


async def _send_logo(msg: Message, prompt_text: str):
    """Pollinations se image download karke bhejo — Telegram URL se
    khud fetch nahi kar pata (generation slow hoti hai). Pollinations
    free limit: 1 image / 45 sec per IP — isliye retries ke beech
    rukna padta hai."""
    prompt = quote(prompt_text)
    urls = [
        f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true",
        f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&seed={random.randint(1, 99999)}",
        f"https://image.pollinations.ai/prompt/{prompt}?nologo=true",
        f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&seed={random.randint(1, 99999)}",
    ]
    delays = [0, 15, 30, 45]
    for url, delay in zip(urls, delays):
        if delay:
            await asyncio.sleep(delay)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=90)
            ) as ses:
                async with ses.get(url) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.read()
            if len(data) < 5000:
                continue
            photo = io.BytesIO(data)
            photo.name = "logo.png"
            await msg.reply_photo(photo=photo)
            return
        except Exception:
            continue
    await msg.reply_text("ʟᴏɢᴏ ɴᴀʜɪ ʙᴀɴᴀ, ᴛʜᴏᴅɪ ᴅᴇʀ ʙᴀᴀᴅ ᴛʀʏ ᴋᴀʀᴏ 😅")


@app.on_message(filters.command("logo"))
async def logo(app, msg: Message):
    if len(msg.command) == 1:
       return await msg.reply_text("Usage:\n\n /logo STRANGER")
    logo_name = msg.text.split(" ", 1)[1]
    # sdbots.tech band ho gaya — ab Pollinations (free AI image) se logo banta hai
    await _send_logo(
        msg,
        f"stylish neon text logo of the word '{logo_name}', glowing letters, "
        "dark background, premium digital art",
    )

@app.on_message(filters.command("animelogo"))
async def animelogo(app, msg: Message):
    if len(msg.command) == 1:
       return await msg.reply_text("Usage:\n\n /animelogo STRANGER")
    logo_name = msg.text.split(" ", 1)[1]
    await _send_logo(
        msg,
        f"anime style text logo of the word '{logo_name}', cute anime girl "
        "character, colorful, vibrant digital art",
    )
