
import math

from BrandrdXMusic.utils.database import is_autoplay
from pyrogram.types import InlineKeyboardButton
from BrandrdXMusic.utils.formatters import time_to_seconds


# Track Markup
def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


# Stream Timer Markup
def stream_markup_timer(_, vidid, chat_id, played, dur):
    try:
        played_sec = time_to_seconds(played) or 0
        duration_sec = time_to_seconds(dur) or 0

        if duration_sec > 0:
            percentage = (played_sec / duration_sec) * 100
        else:
            percentage = 0

        percentage = max(0, min(100, percentage))
        umm = math.floor(percentage)

    except (ValueError, TypeError, ZeroDivisionError):
        umm = 0

    if umm <= 10:
        bar = "❥—————————"
    elif umm < 20:
        bar = "—❥————————"
    elif umm < 30:
        bar = "——❥———————"
    elif umm < 40:
        bar = "———❥——————"
    elif umm < 50:
        bar = "————❥—————"
    elif umm < 60:
        bar = "—————❥————"
    elif umm < 70:
        bar = "——————❥———"
    elif umm < 80:
        bar = "———————❥——"
    elif umm < 95:
        bar = "————————❥—"
    else:
        bar = "—————————❥"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="↻",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▢",
                callback_data=f"ADMIN Stop|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔁 Aᴜᴛᴏ Pʟᴀʏ",
                callback_data=f"autoplay {chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ],
    ]
    return buttons


# Stream Markup
def stream_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="▷",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="↻",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▢",
                callback_data=f"ADMIN Stop|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔁 Aᴜᴛᴏ Pʟᴀʏ",
                callback_data=f"autoplay {chat_id}",
            ),
        ],

        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ],
    ]
    return buttons


# Playlist Markup
def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"Playlists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
                ),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"Playlists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


# Livestream Markup
def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=(
                    f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


# Slider Markup
def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = str(query)[:20]
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=(
                    f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}"
                ),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=(
                    f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}"
                ),
            ),
        ],
    ]
    return buttons
