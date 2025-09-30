import asyncio
import os
import re
import json
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from BrandrdXMusic.utils.database import is_on_off
from BrandrdXMusic.utils.formatters import time_to_seconds



import glob
import random
import logging


# ---------------------- COOKIE HANDLING ---------------------- #
def cookie_txt_file() -> Union[str, None]:
    """Return a random cookies/*.txt file or None if not found."""
    folder_path = os.path.join(os.getcwd(), "cookies")
    os.makedirs(folder_path, exist_ok=True)
    log_file = os.path.join(folder_path, "logs.csv")

    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        return None  # <-- safe return

    cookie_file = random.choice(txt_files)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Chosen File : {cookie_file}\n")

    return cookie_file


# ---------------------- UTILS ---------------------- #
async def check_file_size(link: str):
    cookie_file = cookie_txt_file()
    cmd = ["yt-dlp", "-J", link]
    if cookie_file:
        cmd.insert(1, "--cookies")
        cmd.insert(2, cookie_file)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(f"Error:\n{stderr.decode()}")
        return None

    try:
        info = json.loads(stdout.decode())
        return sum(fmt.get("filesize", 0) for fmt in info.get("formats", []))
    except Exception as e:
        print(f"Parse error: {e}")
        return None


async def shell_cmd(cmd: str):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    if err and "unavailable videos are hidden" not in err.decode().lower():
        return err.decode("utf-8")
    return out.decode("utf-8")


# ---------------------- YOUTUBE API ---------------------- #
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # ---------- Helpers ---------- #
    async def _add_cookies(self, cmd: list):
        cookie_file = cookie_txt_file()
        if cookie_file:
            cmd.insert(1, "--cookies")
            cmd.insert(2, cookie_file)
        return cmd

    async def _safe_ytdl(self, link: str, opts: dict):
        """Run yt-dlp in executor safely"""
        loop = asyncio.get_running_loop()

        def run():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(link, download=False)

        return await loop.run_in_executor(None, run)

    # ---------- Core ---------- #
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link, videoid=None):
        return (await self.details(link, videoid))[0]

    async def duration(self, link, videoid=None):
        return (await self.details(link, videoid))[1]

    async def thumbnail(self, link, videoid=None):
        return (await self.details(link, videoid))[3]

    async def video(self, link, videoid=None):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        cmd = await self._add_cookies(
            ["yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", link]
        )
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, stderr.decode())

    async def playlist(self, link, limit, user_id, videoid=None):
        if videoid:
            link = self.listbase + link
        link = link.split("&")[0]

        cookie_file = cookie_txt_file()
        cookie_arg = f"--cookies {cookie_file}" if cookie_file else ""
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist {cookie_arg} --playlist-end {limit} --skip-download {link}"
        )
        return [x for x in playlist.split("\n") if x.strip()]

    async def track(self, link, videoid=None):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return {
                "title": result["title"],
                "link": result["link"],
                "vidid": result["id"],
                "duration_min": result["duration"],
                "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }, result["id"]

    async def formats(self, link, videoid=None):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        r = await self._safe_ytdl(link, opts)
        formats_available = [
            {
                "format": f.get("format"),
                "filesize": f.get("filesize"),
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "format_note": f.get("format_note"),
                "yturl": link,
            }
            for f in r.get("formats", [])
            if f.get("format") and "dash" not in str(f.get("format")).lower()
        ]
        return formats_available, link

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        loop = asyncio.get_running_loop()

        # ---------- inner downloaders ---------- #
        def audio_dl():
            opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(path):
                    ydl.download([link])
                return path

        def video_dl():
            opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(path):
                    ydl.download([link])
                return path

        # ---------- choose mode ---------- #
        if songvideo:
            await loop.run_in_executor(None, video_dl)
            return f"downloads/{title}.mp4"
        elif songaudio:
            await loop.run_in_executor(None, audio_dl)
            return f"downloads/{title}.mp3"
        elif video:
            if await is_on_off(1):
                direct = True
                file = await loop.run_in_executor(None, video_dl)
            else:
                cmd = await self._add_cookies(
                    ["yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", link]
                )
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    return stdout.decode().split("\n")[0], False
                file = await loop.run_in_executor(None, video_dl)
                direct = True
        else:
            file = await loop.run_in_executor(None, audio_dl)
            direct = True

        return file, direct
