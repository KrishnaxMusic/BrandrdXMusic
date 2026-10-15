import asyncio
import importlib

from pyrogram import filters, idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BrandrdXMusic import LOGGER, app, userbot
from BrandrdXMusic.core.call import Hotty
from BrandrdXMusic.misc import sudo
from BrandrdXMusic.plugins import ALL_MODULES
from BrandrdXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


from pyrogram import filters

@app.on_message(filters.all, group=-9999)
async def debug_all_messages(client, message):
    LOGGER(__name__).info(
        f"INCOMING UPDATE: chat={message.chat.id}, "
        f"text={message.text or message.caption or '<non-text>'}"
    )
    
async def init():
    try:
        if not config.BOT_TOKEN:
            LOGGER(__name__).error("BOT_TOKEN is missing!")
            return

        if not any([
            config.STRING1,
            config.STRING2,
            config.STRING3,
            config.STRING4,
            config.STRING5,
        ]):
            LOGGER(__name__).error(
                "No assistant session configured!"
            )
            return

        await sudo()

        try:
            users = await get_gbanned()
            BANNED_USERS.update(users)

            users = await get_banned_users()
            BANNED_USERS.update(users)
        except Exception:
            LOGGER(__name__).exception(
                "Failed to load banned users"
            )

        # Start bot and verify the actual bot identity.
        await app.start()

        me = await app.get_me()
        LOGGER(__name__).info(
            f"BOT CONNECTED: @{me.username} | ID: {me.id}"
        )

        # Register diagnostic handler BEFORE importing plugins.
        @app.on_message(filters.all, group=-9999)
        async def debug_all_messages(client, message):
            LOGGER(__name__).info(
                "INCOMING UPDATE: "
                f"chat={message.chat.id} "
                f"user={getattr(message.from_user, 'id', None)} "
                f"text={message.text or message.caption or '<non-text>'}"
            )

        # Import all bot plugins.
        for module in ALL_MODULES:
            importlib.import_module(
                "BrandrdXMusic.plugins" + module
            )

        LOGGER(__name__).info("All plugins imported.")

        # Load banned-user lists and start assistant.
        await userbot.start()
        await Hotty.start()

        try:
            await Hotty.stream_call(
                "https://graph.org/file/e999c40cb700e7c684b75.mp4"
            )
        except NoActiveGroupCall:
            LOGGER(__name__).warning(
                "No active voice chat found. "
                "Start a voice chat in the configured log group."
            )
        except Exception:
            LOGGER(__name__).exception(
                "Initial music stream failed; bot will remain running."
            )

        await Hotty.decorators()

        LOGGER(__name__).info(
            "Bot startup complete. Waiting for Telegram updates."
        )

        await idle()

    except Exception:
        LOGGER(__name__).exception("Bot startup/runtime failed")
        raise

    finally:
        try:
            await Hotty.stop()
        except Exception:
            LOGGER(__name__).exception("Failed to stop PyTgCalls")

        try:
            await userbot.stop()
        except Exception:
            LOGGER(__name__).exception("Failed to stop assistant")

        try:
            await app.stop()
        except Exception:
            LOGGER(__name__).exception("Failed to stop bot")

        LOGGER(__name__).info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(init())
