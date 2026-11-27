"""Ishani ki apni AI API (Gemini -> Groq) se text banane ka helper.

Keys .env se aati hain: GEMINI_API_KEY, GROQ_API_KEY.
Pehle Gemini (gemini-3.5-flash-lite) try hota hai, fail ho to Groq
(openai/gpt-oss-20b). Dono fail -> None.
"""

import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

_GEMINI_MODEL = "gemini-3.5-flash-lite"
_GROQ_MODEL = "openai/gpt-oss-20b"


async def _gemini(prompt: str) -> str | None:
    if not GEMINI_API_KEY:
        return None
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{_GEMINI_MODEL}:generateContent"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=25)
        ) as ses:
            async with ses.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None
    except Exception:
        return None


async def _groq(prompt: str) -> str | None:
    if not GROQ_API_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": _GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.9,
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=25)
        ) as ses:
            async with ses.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        return text or None
    except Exception:
        return None


async def ai_text(prompt: str) -> str | None:
    """Prompt bhejo, AI ka jawab text me milega. Dono API fail -> None."""
    text = await _gemini(prompt)
    if text:
        return text
    return await _groq(prompt)
