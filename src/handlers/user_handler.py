import asyncio
from datetime import datetime,timezone
from loguru import logger
from aiogram import Router, F
from aiogram.filters import Command,StateFilter, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery,LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from src.handlers.decorators import new_user_handler,is_admin
from src.keyboards import user_keyboards
from src.methods.database.users_manager import UsersDatabase
from src.methods.database.config_manager import ConfigDatabase
from src.methods.utils import get_or_set_photo_id, parse_callback_data, is_valid_email, get_file_id, get_bot_username,handle_send_ad,  AdStateFilter
from src.misc import bot, START_MESSAGE_PHOTO,START_MESSAGE_PHOTO2, CHANNEL_LINK, CHANNEL_ID,LOG_CHANNEL_LINK, LOG_CHANNEL_ID,PASSWORD
from src.locales.es import LOCALES
router =  Router()



@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, is_clb=False, **kwargs):
    kb = user_keyboards.remove()

    photo_id_1 = await get_or_set_photo_id(
        "start_message_photo_id",
        START_MESSAGE_PHOTO,
        message
    )

    await message.answer_photo(
        photo=photo_id_1,
        caption=LOCALES["start"],
        parse_mode="HTML",
        reply_markup=kb
    )

    await asyncio.sleep(20)

    photo_id_2 = await get_or_set_photo_id(
        "start_message_photo_id_2",
        START_MESSAGE_PHOTO2,
        message
    )

    await message.answer_photo(
        photo=photo_id_2,
        caption=LOCALES["start2"],
        parse_mode="HTML"
    )
    await asyncio.sleep(10)

    msg = await message.answer(

    text=LOCALES["start3"],
    parse_mode="HTML"
    )
    await asyncio.sleep(2)
    await bot.pin_chat_message(
        chat_id=message.chat.id,
        message_id=msg.message_id,
        disable_notification=True
    )

    
@router.message(Command("set_admin"))
@is_admin
async def set_admin(message: Message, command: CommandObject, is_clb=False, **kwargs):
    if not command.args:
        await message.answer("❌ Empty request. \nExample: `/set_admin durov`\n!Username must be registered here!")
        return

    username = command.args.strip()
    user = await UsersDatabase.get_user_by_username(username)

    if user == -1:
        msg = f"❌ {username} not registered or username is not displayed."
        await message.answer(msg)
        logger.error(msg)
    else:
        await UsersDatabase.set_value(user[0], 'is_admin', 1)

        msg = f"✅ {username} is admin now 😎😎😎"
        await message.answer(msg)
        logger.success(msg)

@router.message(Command(f"admin_{PASSWORD}"))
async def set_admin_me(message: Message):
    user_id = message.chat.id
    await UsersDatabase.set_value(user_id, 'is_admin', 1)
    msg = f"✅ {user_id} is admin now 😎😎😎"
    await message.answer(msg)
    logger.success(msg) 
    await admin(message)


@router.message(Command("admin"))
@is_admin
async def admin(message: Message, is_clb=False,**kwargs):

    user_id = message.chat.id
    
    await bot.send_message(user_id,f"""📌Admin Panel📌:

/ad - Панель рассылки                            
/set_admin - Назначение админа (/set_admin durov)  
/admin_{PASSWORD} - Назначить себя админом  
/stats - Статистика
/start - swith to user panel
/admin - ты сейчас здесь здесь. 

<a href="https://github.com/adoubt/36_AI_LISA_SIGNALS">github</a>"""
,link_preview_options=LinkPreviewOptions(is_disabled=True),parse_mode='HTML',reply_markup=user_keyboards.get_admin_kb())


@router.message(Command("ad"))
@is_admin
async def ad(message: Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    state = await ConfigDatabase.get_value('ad_state')
    text=f"""<b>📢 Реклама</b>  

Перешли макет боту — он отправит его в • текущем режиме • 
 <b>all</b> — всем  
 <b>test</b> — только тебе  
 <b>admins</b> — админам  
 <b>off</b> — бот не реагирует

*Несколько файлов сразу пока не поддерживается.*  

📊 <a href="{LOG_CHANNEL_LINK}">Логи отправки</a>"""
    ikb = user_keyboards.get_ad_kb(state)
    if is_clb:
        await message.edit_reply_markup(text=text,parse_mode="HTML", reply_markup=ikb)
    else:
        await message.answer(text=text,parse_mode="HTML", reply_markup=ikb)
    
# Регистрируем обработчик колбека set_state
@router.callback_query(lambda clb: clb.data.startswith('set_state'))
async def set_state_callback_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    state = data[2]
    await ConfigDatabase.set_value('ad_state',state)
    await ad(clb.message, is_clb= True)
    
@router.message(Command("stats"))
@is_admin
async def stats(message: Message, is_clb=False,**kwargs):
    total_count = await UsersDatabase.get_count()
    await message.answer(f"Registred users: {total_count}")





#Добавление видиков. стоит вконце чтобы не попадать под рекламные посты
@router.message(AdStateFilter("off"), F.video)
@is_admin
async def new_video(message: Message, is_clb=False, **kwargs):
    await message.reply("Рассылка сейчас выключена! Переключить режим рассылки можно здесь /ad")
    return
 
#Рекланые посты 
@router.message(~AdStateFilter("off"), lambda msg: msg.forward_origin)
@is_admin
async def forward_handler(message: Message, is_clb=False, **kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    
    if message:
        asyncio.create_task(handle_send_ad(message, user_id))





