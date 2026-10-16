from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils.database import add_sudo, remove_sudo
from BrandrdXMusic.utils.decorators.language import language
from BrandrdXMusic.utils.extraction import extract_user
from BrandrdXMusic.utils.inline import close_markup
from config import BANNED_USERS, OWNER_ID

@app.on_message(filters.command(["addsudo"]) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user.mention))
    added = await add_sudo(user.id)
    if added:
        SUDOERS.add(user.id)
        await message.reply_text(_["sudo_2"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user.mention))
    removed = await remove_sudo(user.id)
    if removed:
        SUDOERS.remove(user.id)
        await message.reply_text(_["sudo_4"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    if message.from_user.id not in SUDOERS:
        return await message.reply_text("💔 <b>ᴏᴡɴᴇʀs:</b>\n1➤ <a href='https://t.me/BRANDED_WORLD'>🇷🇺⛦°𝗕𝗥𝗔𝗡𝗗𝗘𝗗 𓆩🇽𓆪 𝗞𝗜𝗡𝗚🇳</a>",
        disable_web_page_preview=True,
        parse_mode="html")
    text = _["sudo_5"]
    user = await app.get_users(OWNER_ID)
    user = user.first_name if not user.mention else user.mention
    text += f"1➤ {user}\n"
    count = 0
    smex = 0
    for user_id in SUDOERS:
        if user_id != OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += _["sudo_6"]
                count += 1
                text += f"{count}➤ {user}\n"
            except:
                continue
    if not text:
        await message.reply_text(_["sudo_7"])
    else:
        await message.reply_text(text, reply_markup=close_markup(_))


@app.on_callback_query(filters.regex("confirm_delete_all_sudo"))
async def confirm_delete_all_sudoers(client, callback_query: CallbackQuery):
    if not can_use_owner_commands(callback_query.from_user.id):
        return await callback_query.answer("❌ Only owner can do this!", show_alert=True)
    
    deleted_count = 0
    sudoers_to_remove = [user_id for user_id in SUDOERS.copy() if user_id != OWNER_ID]
    
    for user_id in sudoers_to_remove:
        try:
            removed = await remove_sudo(user_id)
            if removed:
                SUDOERS.discard(user_id)
                deleted_count += 1
        except:
            continue
    
    if deleted_count > 0:
        await callback_query.edit_message_text(
            f"✅ <b>Successfully deleted all sudoers!</b>\n\n"
            f"📊 <b>Deleted:</b> <code>{deleted_count}</code> users\n"
            f"🛡️ <b>Protected:</b> Owner remains safe"
        )
    else:
        await callback_query.edit_message_text("❌ <b>Failed to delete sudoers!</b>\n\nTry again later.")


@app.on_callback_query(filters.regex("cancel_delete_all_sudo"))
async def cancel_delete_all_sudoers(client, callback_query: CallbackQuery):
    await callback_query.edit_message_text("❌ <b>Cancelled!</b>\n\nNo sudoers were deleted.")


@app.on_callback_query(filters.regex("view_sudolist_unauthorized"))
async def unauthorized_sudolist_callback(client, callback_query: CallbackQuery):
    await callback_query.answer(
        "🚫 Access Denied!\n\nOnly Owner and Sudoers can check sudolist.", 
        show_alert=True
    )
