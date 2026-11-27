from SHUKLAMUSIC import app
from pyrogram import Client, filters
from SHUKLAMUSIC.utils.ai_helper import ai_text

# Hindi joke ab Ishani ki apni AI API (Gemini -> Groq) se banta hai —
# har baar naya joke. Purani Hindi joke API dono band ho gayi thi.
JOKE_PROMPT = (
    "एक छोटा सा, साफ़-सुथरा हिंदी जोक सुनाओ। जोक 2-4 लाइन का हो, "
    "टीचर-छात्र, डॉक्टर-मरीज़ या पप्पू स्टाइल का। "
    "पूरे जोक को केवल देवनागरी लिपि में लिखो — अंग्रेज़ी (Roman) अक्षरों का "
    "इस्तेमाल बिल्कुल मत करो। सिर्फ़ जोक लिखो, उसके अलावा कुछ मत लिखो — "
    "न intro, न explanation।"
)


@app.on_message(filters.command("hjoke"))
async def joke(_, message):
    joke_text = await ai_text(JOKE_PROMPT)
    if not joke_text:
        joke_text = "ᴀʙʜɪ ᴊᴏᴋᴇ ɴᴀʜɪ ᴍɪʟᴀ, ᴛʜᴏᴅɪ ᴅᴇʀ ʙᴀᴀᴅ ᴛʀʏ ᴋᴀʀᴏ 😅"
    await message.reply_text(joke_text)
