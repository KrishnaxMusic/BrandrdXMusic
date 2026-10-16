import logging
import asyncio
import importlib
from sys import argv

from pyrogram import idle
from pyrogram.raw.types import UpdateGroupCall, PeerChannel, PeerChat
from pytgcalls.exceptions import NoActiveGroupCall

Compatibility patch for py-tgcalls 0.9.7

if not hasattr(UpdateGroupCall, "chat_id"):
def _chat_id(self):
peer = getattr(self, "peer", None)

    if isinstance(peer, PeerChannel):
        return peer.channel_id
    elif isinstance(peer, PeerChat):
        return peer.chat_id

    return None

UpdateGroupCall.chat_id = property(_chat_id)

import config
from BrandrdXMusic import LOGGER, app, userbot
from BrandrdXMusic.core.call import Hotty
from BrandrdXMusic.misc import sudo
from BrandrdXMusic.plugins import ALL_MODULES
from BrandrdXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

async def init():
if (
not config.STRING1
and not config.STRING2
and not config.STRING3
and not config.STRING4
and not config.STRING5
):
LOGGER(name).error(
"Assistant client variables not defined, exiting..."
)
exit()

await sudo()

try:
    users = await get_gbanned()
    for user_id in users:
        BANNED_USERS.add(user_id)

    users = await get_banned_users()
    for user_id in users:
        BANNED_USERS.add(user_id)
except Exception:
    pass

await app.start()

for all_module in ALL_MODULES:
    importlib.import_module("BrandrdXMusic.plugins" + all_module)

LOGGER("BrandrdXMusic.plugins").info(
    "Successfully Imported Modules..."
)

await userbot.start()
await Hotty.start()

try:
    await Hotty.stream_call(
        "https://graph.org/file/e999c40cb700e7c684b75.mp4"
    )
except NoActiveGroupCall:
    LOGGER("BrandrdXMusic").error(
        "Please turn on the videochat of your log group/channel.\n\n"
        "Stopping Bot..."
    )
    exit()
except Exception:
    pass

await Hotty.decorators()

LOGGER("BrandrdXMusic").info(
    "ᴅʀᴏᴘ ʏᴏᴜʀ ɢɪʀʟꜰʀɪᴇɴᴅ'ꜱ ɴᴜᴍʙᴇʀ ᴀᴛ @BRANDED_PAID_CC "
    "ᴊᴏɪɴ @BRANDRD_BOT , @BRANDED_WORLD ꜰᴏʀ ᴀɴʏ ɪꜱꜱᴜᴇꜱ"
)

await idle()
await app.stop()
await userbot.stop()

LOGGER("BrandrdXMusic").info("Stopping Brandrd Music Bot...")

if name == "main":
asyncio.get_event_loop().run_until_complete(init())
