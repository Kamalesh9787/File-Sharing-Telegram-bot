
<<<<<<< HEAD
=======
from bot import Bot
from config import ADMINS, FORCE_MSG, OWNER_TAG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, OWNER_ID, CHANNEL_LINK, FORCE_SUB_CHANNEL2
from helper_func import subscribed, subscribed2, decode, get_messages, removeDuplicates
from database.database import add_user, del_user, full_userbase, present_user

# Time in seconds for auto-deleting the sent messages
SECONDS = 60  # 1 minutes

@Bot.on_message(filters.command('start') & filters.private & subscribed & subscribed2)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        sent_messages = []

        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                sent_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                sent_messages.append(sent_msg)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                sent_messages.append(sent_msg)
            except:
                pass
        
        notification_msg = await message.reply(f"<b>❗️ <u>Notice</u> ❗️</b>\n\n<b>This file will be deleted in {SECONDS // 60} minutes. Please save it before it gets deleted.</b>")
        await asyncio.sleep(SECONDS)
        for sent_msg in sent_messages:
            try:
                await sent_msg.delete()
            except:
                pass
        await notification_msg.edit("<b>Your file has been successfully deleted!</b>")
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data="about"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

    
#=====================================================================================##

WAIT_MSG = """<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message without any spaces.</code>"""

#=====================================================================================##

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    if FORCE_SUB_CHANNEL2:    
        buttons = [
            [
                InlineKeyboardButton(
                    "Join Channel",
                    url=client.invitelink),
                InlineKeyboardButton(
                    "Join Channel",
                    url=client.invitelink2),
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    "Join Channel",
                    url=client.invitelink),
            ]
        ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

@Bot.on_message(filters.command('auth_secret') & filters.user(ADMINS))
async def add_admin(client: Bot, message: Message):
    _, _, user_id = message.text.partition(' ')
    try:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)]
            ]
        )
        await message.reply("User has been added as an admin.")
        await client.send_message(
            chat_id=user_id,
            text=f"You are verified, join the channel for forwarding links for batch commands.",
            reply_markup=reply_markup
        )

    except Exception as e:
        await message.reply("Failed to verify user. Please ensure the user ID is correct and that they have started the bot.")


@Bot.on_message(filters.command('auth') & filters.private)
async def auth_command(client: Bot, message: Message):
    await client.send_message(
        chat_id=OWNER_ID,
        text=f"Message for @{OWNER_TAG}\n<code>/auth_secret {message.from_user.id}</code>",
    )

    await message.reply("Please wait for verification from the owner.")
>>>>>>> eb1741bee2807923fb677dcf0011700f4432f973