from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from urllib.parse import parse_qs, unquote, urlparse

from search_engine_parser.core.engines.duckduckgo import Search as DDGSearch
from SHUKLAMUSIC import app

# Google Custom Search ki key band ho gayi thi (403) — ab DuckDuckGo se
# t.me links search hote hain (free, bina key).
ddg = DDGSearch()
PAGE_SIZE = 10


def _clean_link(link: str) -> str:
    link = str(link or "")
    if "uddg=" in link:
        qs = parse_qs(urlparse(link).query)
        real = (qs.get("uddg") or [""])[0]
        if real:
            return unquote(real)
    if link.startswith("//"):
        return "https:" + link
    return link


async def _search_tg(query: str):
    """t.me results ki list [(title, link), ...] — duplicates hataye hue."""
    items = []
    seen = set()
    for q in (f"site:t.me {query}", f"t.me {query}"):
        try:
            result = await ddg.async_search(q)
        except Exception:
            continue
        for i in range(len(result)):
            try:
                title = result[i]["titles"]
                link = _clean_link(result[i]["links"])
            except Exception:
                continue
            if "t.me/" not in link:
                continue
            link = link.split("?")[0].rstrip("/")
            link = re.sub(r"/\d+$", "", link)
            if link in seen:
                continue
            seen.add(link)
            items.append((title, link))
        if items:
            break
    return items


def _page_text(items, page: int) -> str:
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]
    return "\n\n".join(f"{t}\n{l}" for t, l in chunk)


def _page_buttons(query: str, page: int, total: int):
    btns = []
    if page > 0:
        btns.append(
            InlineKeyboardButton("◀️Prev◀️", callback_data=f"tgprev {page-1} {query}")
        )
    if (page + 1) * PAGE_SIZE < total:
        btns.append(
            InlineKeyboardButton("▶️Next▶️", callback_data=f"tgnext {page+1} {query}")
        )
    return InlineKeyboardMarkup([btns]) if btns else None


@app.on_message(filters.command("tg"))
async def search_command(_, message):
    if len(message.text.split()) < 2:
        return await message.reply("Usage: /tg <group name>")
    query = message.text.split(None, 1)[1]
    msg = await message.reply("Searching...")
    items = await _search_tg(query)
    if not items:
        return await msg.edit("No results found!")
    await msg.edit(
        _page_text(items, 0),
        reply_markup=_page_buttons(query, 0, len(items)),
    )


@app.on_callback_query(filters.regex(r"tg(prev|next) (\d+) (.+)"))
async def tg_page_callback(_, callback_query):
    parts = callback_query.data.split(None, 2)
    page = int(parts[1])
    query = parts[2]
    items = await _search_tg(query)
    if not items or page * PAGE_SIZE >= len(items):
        return await callback_query.answer("No more results!")
    await callback_query.edit_message_text(
        _page_text(items, page),
        reply_markup=_page_buttons(query, page, len(items)),
    )
