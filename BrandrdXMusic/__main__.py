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


# Register handlers BEFORE starting the Telegram client.
@app.on_message(filters.command("start"), group=-9999)
async def fallback_start(client, message):
    LOGGER(__name__).info("FALLBACK /start HANDLER TRIGGERED")
    await message.reply_text(
        "Music Bot is online! 🎵\n\n"
        "Send /help to see available commands."
    )


@app.on_message(filters.all, group=-9998)
async def debug_updates(client, message):
    LOGGER(__name__).info(
        "INCOMING UPDATE: "
        f"chat={message.chat.id}, "
        f"text={message.text or message.caption or '<non-text>'}"
    )


async def init():
    bot_started = False
    assistant_started = False
    call_started = False

    try:
        if not config.BOT_TOKEN:
            raise RuntimeError("BOT_TOKEN is missing")

        if not any([
            config.STRING1, config.STRING2, config.STRING3,
            config.STRING4, config.STRING5
        ]):
            raise RuntimeError("At least one assistant STRING is required")

        await sudo()

        try:
            BANNED_USERS.update(await get_gbanned())
            BANNED_USERS.update(await get_banned_users())
        except Exception:
            LOGGER(__name__).exception("Could not load banned users")

        await app.start()
        bot_started = True

        me = await app.get_me()
        LOGGER(__name__).info(
            f"BOT CONNECTED: @{me.username} | ID: {me.id}"
        )

        for module in ALL_MODULES:
            importlib.import_module("BrandrdXMusic.plugins" + module)

        LOGGER(__name__).info("All plugins imported.")

        await userbot.start()
        assistant_started = True

        await Hotty.start()
        call_started = True

        try:
            await Hotty.stream_call(
                "https://graph.org/file/e999c40cb700e7c684b75.mp4"
            )
        except NoActiveGroupCall:
            LOGGER(__name__).warning(
                "No active voice chat; music streaming is unavailable "
                "until a voice chat is started."
            )
        except Exception:
            LOGGER(__name__).exception(
                "Initial stream failed; keeping bot online."
            )

        await Hotty.decorators()
        LOGGER(__name__).info("Startup complete; waiting for updates.")
        await idle()

    except Exception:
        LOGGER(__name__).exception("Bot startup/runtime failed")
        raise

    finally:
        if call_started:
            try:
                await Hotty.stop()
            except Exception:
                LOGGER(__name__).exception("Failed to stop call client")

        if assistant_started:
            try:
                await userbot.stop()
            except Exception:
                LOGGER(__name__).exception("Failed to stop assistant")

        if bot_started:
            try:
                await app.stop()
            except Exception:
                LOGGER(__name__).exception("Failed to stop Telegram bot")


if __name__ == "__main__":
    asyncio.run(init())
