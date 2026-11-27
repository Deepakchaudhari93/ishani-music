import os
import re
import time
import asyncio
import config
import aiohttp
import logging
import yt_dlp
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

log = logging.getLogger("youtube")
RITESH_KEY = config.MUSIC_API_KEY
RITESH_BASE = config.RITESH_API_BASE
AARUSH_BASE = getattr(config, "AARUSH_API_BASE", "https://aarush-support-api.hostless.app")
AARUSH_KEY = getattr(config, "AARUSH_API_KEY", "")
YUKI_BASE = getattr(config, "YUKI_API_BASE", "https://music.yukiapi.site")
YUKI_KEY = getattr(config, "YUKI_API_KEY", "")
BABY_API_BASE = "https://baby-music-api.vercel.app/api/play"

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        text, offset = "", None
        for message in messages:
            if offset is not None: break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text, offset, length = message.text or message.caption, entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK: return entity.url
        if offset is not None: return text[offset : offset + length]
        return None

    def extract_vidid(self, link: str) -> str:
        if "youtu.be/" in link: return link.split("youtu.be/")[1].split("?")[0].split("&")[0]
        elif "v=" in link: return link.split("v=")[1].split("&")[0].split("?")[0]
        elif "shorts/" in link: return link.split("shorts/")[1].split("?")[0].split("&")[0]
        return link.split("/")[-1].split("?")[0]

    # ─── SEARCH ───────────────────────────────────────────────────────────────
    # query_lower -> (ts, details, vidid); repeat gaane search skip
    _track_cache = {}

    async def _yuki_track(self, link: str):
        """Yuki se details/search. Fail ho to None (race mein haar jayega)."""
        try:
            if "youtu" in link:
                vid_id = self.extract_vidid(link)
                det = await self._yuki_info(vid_id)
                if det:
                    return det, det["vidid"]
            else:
                results = await self._yuki_search(link, limit=1)
                if results:
                    return results[0], results[0]["vidid"]
        except Exception:
            pass
        return None

    async def _ritesh_track(self, link: str):
        """Ritesh se details/search. Fail ho to None."""
        if "youtu" in link:
            vid_id = self.extract_vidid(link)
            url = f"{RITESH_BASE}/details?link={vid_id}&api_key={RITESH_KEY}"
        else:
            url = f"{RITESH_BASE}/search?q={link.replace(' ', '+')}&limit=1&api_key={RITESH_KEY}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "youtu" in link and "title" in data:
                            return {"title": data["title"], "link": data["link"], "vidid": data["vidid"], "duration_min": data["duration_min"], "thumb": data["thumbnail"]}, data["vidid"]
                        elif not "youtu" in link and data.get("result"):
                            r = data["result"][0]
                            return {"title": r["title"], "link": r["link"], "vidid": r["id"], "duration_min": r["duration"], "thumb": r["thumbnails"][0]["url"]}, r["id"]
        except Exception as e:
            log.warning(f"API Search failed: {e}")
        return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link

        # 0) Memory cache — wahi gaana dobara maanga jaye to search hi
        # skip (30 min tak). Speed ke liye (2026-11-27).
        cache_key = link.strip().lower()
        hit = self._track_cache.get(cache_key)
        if hit and time.monotonic() - hit[0] < 1800:
            return hit[1], hit[2]

        # 1) Yuki + Ritesh PARALLEL race — jo pehle jawab de, wahi.
        # Pehle serial tha: Yuki fail (0.3s) phir Ritesh — ab dono
        # saath chalte hain, slow wala haar jata hai. (2026-11-27)
        tasks = [
            asyncio.ensure_future(self._yuki_track(link)),
            asyncio.ensure_future(self._ritesh_track(link)),
        ]
        result = None
        try:
            pending = set(tasks)
            while pending and result is None:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_COMPLETED
                )
                for t in done:
                    try:
                        r = t.result()
                    except Exception:
                        r = None
                    if r:
                        result = r
                        break
        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()
        if result:
            if len(self._track_cache) > 300:
                self._track_cache.clear()
            self._track_cache[cache_key] = (time.monotonic(), result[0], result[1])
            return result

        try:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                return {"title": result["title"], "link": result["link"], "vidid": result["id"], "duration_min": result["duration"], "thumb": result["thumbnails"][0]["url"].split("?")[0]}, result["id"]
        except: pass

        vid_id = self.extract_vidid(link) if "youtu" in link else link
        return {"title": "Unknown Song", "link": f"https://youtu.be/{vid_id}", "vidid": vid_id, "duration_min": "00:00", "thumb": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"}, vid_id

    async def details(self, link: str, videoid: Union[bool, str] = None):
        det, _ = await self.track(link, videoid)
        return det["title"], det["duration_min"], int(config.time_to_seconds(det["duration_min"])), det["thumb"], det["vidid"]

    async def title(self, link: str, videoid: Union[bool, str] = None): return (await self.track(link, videoid))[0]["title"]
    async def duration(self, link: str, videoid: Union[bool, str] = None): return (await self.track(link, videoid))[0]["duration_min"]
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None): return (await self.track(link, videoid))[0]["thumb"]

    # ─── STREAMING (WARP + POT + yt-dlp) ──────────────────────────────────────
    # --- STREAMING (Yuki-first, Ritesh second, Aarush third, Baby, yt-dlp) ---
    async def _aarush_direct(self, vid_id: str, video: bool) -> str | None:
        """Aarush Support (apni API) /download endpoint. Query = video ID.
        JSON mein download_url aata hai (JioSaavn fast-path ya YouTube).
        Audio ~1-2s, video YouTube se. Key na ho to skip (Ritesh backup hai)."""
        if not AARUSH_KEY:
            return None
        dl_type = "video" if video else "audio"
        url = f"{AARUSH_BASE}/download?query={vid_id}&dl_type={dl_type}&api_key={AARUSH_KEY}"
        timeout = aiohttp.ClientTimeout(total=60 if video else 25, connect=5)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as r:
                    if r.status != 200:
                        log.warning(f"Aarush download {dl_type} {vid_id} status {r.status}")
                        return None
                    data = await r.json(content_type=None)
                    direct = (data or {}).get("download_url") or ""
                    if direct and str(direct).startswith(("http://", "https://")):
                        return str(direct)
                    return None
        except Exception as e:
            log.warning(f"Aarush download failed {vid_id} {dl_type}: {e}")
            return None

    async def _yuki_direct(self, vid_id: str, video: bool = False) -> str | None:
        """Yuki API (music.yukiapi.site) — /stream/{id} seedha stream
        deta hai, isliye URL hi kaafi hai (player wahi se stream karta
        hai). Audio aur video dono (type param se). Verified 2026-11-27:
        audio 200 ~0.04s (cached), video 206 video/mp4 ~2.6s.
        Backup host play.yukiapi.site band tha (503) — Ishani ke
        kehne par 2026-11-27 ko hata diya, sirf main host hai.
        Key .env mein YUKI_API_KEY se aati hai."""
        if not YUKI_KEY or not vid_id:
            return None
        dl_type = "video" if video else "audio"
        return f"{YUKI_BASE}/stream/{vid_id}?key={YUKI_KEY}&type={dl_type}"

    async def _yuki_search(self, query: str, limit: int = 1) -> list:
        """Yuki /api/search — normalized list [{title, link, vidid,
        duration_min, thumb}] ya khaali list. 2026-11-27 ko endpoint
        503 de raha tha (Yuki ki taraf se down), isliye chhota timeout
        rakha hai: fail ho to caller turant Ritesh backup par jata hai.
        Response format kabhi live 200 mein nahi dekha, isliye parsing
        defensive hai — aam shapes (result/results/items/data list,
        id/videoId/vidid, duration/duration_min/length) sab handle."""
        if not YUKI_KEY or not query:
            return []
        import urllib.parse
        q = urllib.parse.quote_plus(query)
        url = f"{YUKI_BASE}/api/search?q={q}&key={YUKI_KEY}"
        timeout = aiohttp.ClientTimeout(total=4, connect=3)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as r:
                    if r.status != 200:
                        log.warning(f"Yuki search status {r.status} for {query!r}")
                        return []
                    data = await r.json(content_type=None)
        except Exception as e:
            log.warning(f"Yuki search failed for {query!r}: {e}")
            return []
        items = []
        if isinstance(data, dict):
            for k in ("result", "results", "items", "data", "videos"):
                if isinstance(data.get(k), list):
                    items = data[k]
                    break
        elif isinstance(data, list):
            items = data
        out = []
        for it in items[:limit]:
            if not isinstance(it, dict):
                continue
            vid = it.get("id") or it.get("videoId") or it.get("vidid") or it.get("video_id")
            if not vid:
                continue
            thumb = it.get("thumbnail") or it.get("thumb") or ""
            if not thumb and isinstance(it.get("thumbnails"), list) and it["thumbnails"]:
                first = it["thumbnails"][0]
                thumb = first.get("url", "") if isinstance(first, dict) else str(first)
            if not thumb:
                thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            out.append({
                "title": it.get("title") or it.get("name") or "Unknown Song",
                "link": it.get("link") or it.get("url") or f"https://youtu.be/{vid}",
                "vidid": vid,
                "duration_min": it.get("duration_min") or it.get("duration") or it.get("length") or "00:00",
                "thumb": thumb,
            })
        return out

    async def _yuki_info(self, vid_id: str) -> dict | None:
        """Yuki /info/{id} — 2026-11-27 ko 404 de raha tha; chhota
        timeout ke saath try karo, mile to normalized dict, warna None
        (caller Ritesh details par jata hai)."""
        if not YUKI_KEY or not vid_id:
            return None
        url = f"{YUKI_BASE}/info/{vid_id}?key={YUKI_KEY}"
        timeout = aiohttp.ClientTimeout(total=4, connect=3)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as r:
                    if r.status != 200:
                        return None
                    data = await r.json(content_type=None)
        except Exception:
            return None
        if not isinstance(data, dict) or not data.get("title"):
            return None
        thumb = data.get("thumbnail") or data.get("thumb") or ""
        if not thumb and isinstance(data.get("thumbnails"), list) and data["thumbnails"]:
            first = data["thumbnails"][0]
            thumb = first.get("url", "") if isinstance(first, dict) else str(first)
        if not thumb:
            thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
        return {
            "title": data["title"],
            "link": data.get("link") or data.get("url") or f"https://youtu.be/{vid_id}",
            "vidid": data.get("vidid") or data.get("id") or vid_id,
            "duration_min": data.get("duration_min") or data.get("duration") or data.get("length") or "00:00",
            "thumb": thumb,
        }

    async def _ritesh_direct(self, vid_id: str, video: bool) -> str | None:
        """Ritesh /download endpoint, following the 307 to the mp3/mp4.
        Verified 2026-11-19: audio works for NT0fqDDLDms, RzJmBo-2GKI,
        prrmQ4RtMpA, 7VrG_qkWSX8. Video can take ~30s to generate for
        uncached IDs, so use a long timeout."""
        dl_type = "video" if video else "audio"
        url = f"{RITESH_BASE}/download?query={vid_id}&dl_type={dl_type}&api_key={RITESH_KEY}"
        timeout = aiohttp.ClientTimeout(total=60 if video else 20, connect=5)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as r:
                    if r.status != 200:
                        log.warning(f"Ritesh download {dl_type} {vid_id} status {r.status}")
                        return None
                    final = str(r.url)
                    if not final.startswith(("http://", "https://")):
                        return None
                    # No HEAD probe here: the GET already returned 200 and
                    # the final URL, and the probe never changed the result
                    # (the code returned `final` either way) — it only added
                    # up to 6s to every song. Return the URL straight away.
                    return final
        except Exception as e:
            log.warning(f"Ritesh download failed {vid_id} {dl_type}: {e}")
            return None

    async def _baby_direct(self, title: str) -> str | None:
        """Baby music API (Saavn CDN). Audio-only; returns a direct AAC URL.
        Query is the song TITLE (name search), not a video ID. Verified
        2026-11-20: /api/play?song=kalank&quality=720 -> stream_url on
        aac.saavncdn.com (audio/mp4, 320kbps). A different host from
        YouTube, so it is not hit by the YouTube/VPS block."""
        if not title or title == "Unknown Song":
            return None
        import urllib.parse
        q = urllib.parse.quote_plus(title)
        url = f"{BABY_API_BASE}?song={q}&quality=720"
        timeout = aiohttp.ClientTimeout(total=12, connect=5)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as r:
                    if r.status != 200:
                        log.warning(f"Baby API status {r.status} for {title!r}")
                        return None
                    data = await r.json()
                    stream_url = data.get("stream_url") or (data.get("stream") or {}).get("url")
                    if stream_url and str(stream_url).startswith(("http://", "https://")):
                        return str(stream_url)
                    return None
        except Exception as e:
            log.warning(f"Baby API failed for {title!r}: {e}")
            return None

    async def _url_ok(self, url: str) -> bool:
        """Fast check that a stream URL is really fetchable from this VPS.
        Range GET for 1 byte; 200/206 means playable. Catches dead,
        expired or YouTube-blocked URLs that would otherwise join the VC
        and play silence ('no sound') even though the card shows."""
        timeout = aiohttp.ClientTimeout(total=6, connect=3)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers={"Range": "bytes=0-0"}) as r:
                    return r.status in (200, 206)
        except Exception:
            return False

    async def download(self, link: str, mystic, video: Union[bool, str] = None, **kwargs) -> str:
        vid_arg = kwargs.get("videoid")
        if vid_arg:
            # videoid is a flag (True) meaning `link` is a bare video ID,
            # or the ID string itself; either way build the URL from the ID.
            # (Was: self.base + videoid, which raised TypeError when the
            # caller passed videoid=True, breaking every autoplay/queue
            # track — the sibling functions use self.base + link.)
            link = self.base + (vid_arg if isinstance(vid_arg, str) else link)

        vid_id = self.extract_vidid(link) if "youtu" in link else link

        # 0) Yuki API sabse pehle — audio aur video dono (Ishani ki
        # pasand: Yuki first, Ritesh second, Aarush third). URL verify
        # karke hi bajao (dead URL = VC mein silence). Fail ho to
        # Ritesh hai. Video bhi verified 2026-11-27 (206 video/mp4).
        # (Backup host play.yukiapi.site 2026-11-27 ko band tha —
        # Ishani ke kehne par hata diya.)
        direct = await self._yuki_direct(vid_id, bool(video))
        if direct and await self._url_ok(direct):
            log.info(f"Yuki stream OK for {vid_id} video={bool(video)}")
            return direct, True
        if direct:
            log.warning(f"Yuki URL failed verification for {vid_id}, trying Ritesh")

        # 1) Ritesh - but VERIFY the URL is really fetchable from
        # this VPS. A googlevideo URL that looks fine can be dead/blocked
        # by the time pytgcalls fetches it, and then the VC plays silence
        # ("no sound") even though the card shows. A failed verification
        # falls through to the next API instead of playing silence.
        direct = await self._ritesh_direct(vid_id, bool(video))
        if direct and await self._url_ok(direct):
            return direct, True
        if direct:
            log.warning(f"Ritesh URL failed verification for {vid_id}, trying Aarush")

        # 1a) Aarush Support (apni API) backup — Ritesh ke baad.
        direct = await self._aarush_direct(vid_id, bool(video))
        if direct and await self._url_ok(direct):
            return direct, True
        if direct:
            log.warning(f"Aarush URL failed verification for {vid_id}, trying Baby API")

        # 1b) Baby API (Saavn CDN, audio only). Fast and not YouTube-blocked,
        # so it rescues songs when Ritesh is slow/failing, without waiting
        # on bot-blocked yt-dlp. Needs the song TITLE (name search).
        if not video:
            title = None
            try:
                det, _ = await asyncio.wait_for(self.track(link), timeout=10)
                title = (det or {}).get("title")
            except Exception:
                title = None
            if title:
                baby = await self._baby_direct(title)
                if baby and await self._url_ok(baby):
                    return baby, True
                if baby:
                    log.warning(f"Baby API URL failed verification for {title!r}")

        # 2) yt-dlp (now AFTER the APIs): new POT arg name, JS runtime enabled, multiple formats/clients
        cookie_file = None
        if os.path.exists("cookies.txt"):
            cookie_file = "cookies.txt"
        elif os.path.exists("SHUKLAMUSIC/cookies.txt"):
            cookie_file = "SHUKLAMUSIC/cookies.txt"

        # Trimmed for speed: only the most likely combos (2 formats x
        # 2 clients x proxy-ON = 4 tries max). The old 5x5x2=50 attempts
        # each took seconds and yt-dlp is almost always bot-blocked here,
        # so a Ritesh outage hung the song for minutes. Fail fast instead.
        audio_formats = [
            "bestaudio[ext=m4a]/bestaudio/best",
            "bestaudio/best",
        ]
        video_formats = [
            "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best",
            "best[height<=720]/best",
        ]
        formats = video_formats if video else audio_formats
        clients = [["web"], ["android"]]

        for fmt in formats:
            for clients_list in clients:
                for use_proxy in (True,):
                    ydl_opts = {
                        "quiet": True,
                        "no_warnings": True,
                        "nocheckcertificate": True,
                        "format": fmt,
                        "extractor_args": {
                            "youtubepot-bgutilhttp": {"base_url": "http://127.0.0.1:4416"},
                            "youtube": {"player_client": clients_list},
                        },
                        "js_runtimes": {"node": {}},
                        "remote_components": "ejs:github",
                    }
                    if use_proxy:
                        ydl_opts["proxy"] = "http://127.0.0.1:40000"
                    if cookie_file:
                        ydl_opts["cookiefile"] = cookie_file
                    try:
                        def _extract(opts=ydl_opts):
                            with yt_dlp.YoutubeDL(opts) as ydl:
                                info = ydl.extract_info(link, download=False)
                                if info.get("url"):
                                    return info["url"]
                                fmts = info.get("formats") or []
                                if fmts:
                                    return fmts[-1].get("url")
                                return None
                        stream_url = await asyncio.to_thread(_extract)
                        if stream_url:
                            return stream_url, True
                    except Exception as e:
                        log.warning(f"yt-dlp failed fmt={fmt} clients={clients_list} proxy={use_proxy}: {e}")
                        continue

        # 3) Last resort: Ritesh /download URL itself (ffmpeg follows the 307).
        # NOTE: the old /api/musicbot/play/<id> endpoint returns empty - do not use it.
        dl_type = "video" if video else "audio"
        return f"{RITESH_BASE}/download?query={vid_id}&dl_type={dl_type}&api_key={RITESH_KEY}", True

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + videoid
        try:
            url, _ = await self.download(link, None, video=True)
            return 1, url
        except Exception as e:
            raise Exception(f"Video play error: {e}")

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RITESH_BASE}/playlist?link={link}&limit={limit}&api_key={RITESH_KEY}") as resp:
                    data = await resp.json()
            return [v["vidid"] for v in data.get("videos", [])]
        except: return []

    async def formats(self, link: str, videoid: Union[bool, str] = None): return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        # Yuki search pehle, Ritesh backup (2026-11-27).
        results = await self._yuki_search(link, limit=10)
        if results and query_type < len(results):
            r = results[query_type]
            return r["title"], r["duration_min"], r["thumb"], r["vidid"]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RITESH_BASE}/search?q={link.replace(' ', '+')}&limit=10&api_key={RITESH_KEY}") as resp:
                    data = await resp.json()
            r = data["result"][query_type]
            return r["title"], r["duration"], r["thumbnails"][0]["url"], r["id"]
        except:
            return "Unknown", "00:00", config.YOUTUBE_IMG_URL, self.extract_vidid(link)

    async def related(self, vidid: str, exclude: list = None):
        """Autoplay ke liye (Mahi_X_Music wala system): diye gaye vidid ki
        YouTube 'Radio/Mix' playlist (RD<vidid>) se ek similar/related
        video dhoondta hai. `exclude` me jo vidid already play ho chuke
        hain wo diye jayein, taaki wahi gaana repeat na ho.
        Returns: (related_vidid, related_title) ya None agar kuch na mile."""
        exclude_set = set(exclude or [])
        exclude_set.add(vidid)

        cookie_file = None
        if os.path.exists("cookies.txt"):
            cookie_file = "cookies.txt"
        elif os.path.exists("SHUKLAMUSIC/cookies.txt"):
            cookie_file = "SHUKLAMUSIC/cookies.txt"

        loop = asyncio.get_event_loop()

        def _fetch(url):
            # VPS par direct yt-dlp bot-blocked hai — wahi WARP proxy +
            # POT + cookies setup jo download() ke yt-dlp path me hai.
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": True,
                "playlistend": 20,
                "nocheckcertificate": True,
                "extractor_args": {
                    "youtubepot-bgutilhttp": {"base_url": "http://127.0.0.1:4416"},
                },
                "js_runtimes": {"node": {}},
                "remote_components": "ejs:github",
                "proxy": "http://127.0.0.1:40000",
            }
            if cookie_file:
                opts["cookiefile"] = cookie_file
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False) or {}

        # 1) YouTube Radio/Mix (RD<vidid>) — asli related gaane
        try:
            info = await loop.run_in_executor(
                None, _fetch, f"{self.base}{vidid}&list=RD{vidid}"
            )
        except Exception:
            info = {}
        for entry in info.get("entries") or []:
            if not entry:
                continue
            vid = entry.get("id")
            if not vid or vid in exclude_set:
                continue
            return vid, entry.get("title") or "Unknown Title"

        # 2) Fallback: Mix na mile to seed ke title se search karke
        # koi aur gaana try karo, taaki autoplay khaali haath na aaye.
        # Yuki search pehle, Ritesh backup (2026-11-27).
        try:
            det_title = await self.title(vidid, videoid=True)
        except Exception:
            det_title = ""
        if det_title:
            for item in await self._yuki_search(det_title, limit=10):
                vid = item.get("vidid")
                if not vid or vid in exclude_set:
                    continue
                return vid, item.get("title") or "Unknown Title"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{RITESH_BASE}/search?q={det_title.replace(' ', '+')}&limit=10&api_key={RITESH_KEY}",
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        data = await resp.json(content_type=None)
                for item in (data or {}).get("result") or []:
                    vid = item.get("id")
                    if not vid or vid in exclude_set:
                        continue
                    return vid, item.get("title") or "Unknown Title"
            except Exception:
                pass
        return None