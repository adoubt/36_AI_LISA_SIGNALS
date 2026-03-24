import urllib.parse
import re
import asyncio
from aiogram.filters import Filter
from aiogram.types import Message, ContentType
from aiogram import Bot
from src.misc import bot,CHANNEL_ID,LOG_CHANNEL_LINK, LOG_CHANNEL_ID
from src.methods.database.users_manager import UsersDatabase
from src.methods.database.config_manager import ConfigDatabase
from loguru import logger


async def get_or_set_photo_id(key: str, file_path: str, message: Message):
    photo_id = await ConfigDatabase.get_value(key)

    if photo_id:
        return photo_id

    msg = await message.answer_photo(photo=file_path)
    photo_id = msg.photo[-1].file_id

    await ConfigDatabase.set_value(key, photo_id)
    return photo_id

def get_file_id(message: Message, file_type: str) -> str:
    """Проверка основного сообщения"""
    if message.audio and file_type in ['mp3', 'preview']:
        return message.audio.file_id
    elif message.document and file_type in ['wav', 'stems']:
        return message.document.file_id
    #Проверка вложенного сообщения
    elif message.reply_to_message:
        if message.reply_to_message.audio and file_type in ['mp3', 'preview']:
            return message.reply_to_message.audio.file_id
        elif message.reply_to_message.document and file_type in ['wav', 'stems']:
            return message.reply_to_message.document.file_id
    return None

def parse_callback_data(data: str) -> dict:
    """Удаляем префикс и парсим параметры"""
    query_string = data.split(':', 1)[1]
    return dict(urllib.parse.parse_qsl(query_string))

def is_valid_email(email):
    """Определение шаблона для валидации email-адреса"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)






async def is_user_subscribed(user_id: int, **kwargs):

    member = await bot.get_chat_member(int(CHANNEL_ID), user_id)
    if member.status in ["member", "creator", "administrator"]:
        return True
    else:
        return False
    

async def get_bot_username(bot: Bot):
    me = await bot.get_me()
    return me.username 



class AdStateFilter(Filter):
    def __init__(self, required_state: str):
        self.required_state = required_state

    async def __call__(self, message: Message) -> bool:
        state = await ConfigDatabase.get_value("ad_state")
        return state == self.required_state 
    

async def send_ad_message(user_id, message: Message):
    """ Отправляет сообщение конкретному пользователю """
    try:
        if message.content_type == ContentType.TEXT:
            await bot.send_message(user_id, message.html_text, parse_mode="HTML")
        elif message.content_type == ContentType.PHOTO:
            await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.html_text, parse_mode="HTML")
        elif message.content_type == ContentType.VIDEO:
            await bot.send_video(user_id, message.video.file_id, caption=message.html_text, parse_mode="HTML")
        elif message.content_type == ContentType.ANIMATION:
            await bot.send_animation(user_id, message.animation.file_id, caption=message.html_text, parse_mode="HTML")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке {user_id}: {e}")
        return False

async def handle_send_ad(message: Message, admin: int):
    state = await ConfigDatabase.get_value("ad_state")
    users = {
        "all": await UsersDatabase.get_all(),
        "test": [[admin]],
        "admins": await UsersDatabase.get_all_admins()
    }.get(state, [])

    sent_count = 0

    for user in users:
        try:
            success = await send_ad_message(user[0], message)
            if success:
                sent_count += 1
        except Exception:
            pass

        await asyncio.sleep(0.04)

    admin_name = await UsersDatabase.get_value(admin, 'username')
    msg = f"📢 Messages sent: <b>{sent_count}</b>\nSender: @{admin_name} {admin}\nstate: <b>{state}<b>"

    if LOG_CHANNEL_ID:
        try:
            await bot.send_message(
                int(LOG_CHANNEL_ID),
                msg,
                parse_mode="HTML",
                disable_notification=True
            )
        except Exception as e:
            logger.warning(f"LOG_CHANNEL_ID error: {e}")

    logger.success(msg)

