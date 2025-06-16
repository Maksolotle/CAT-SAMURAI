import asyncio
import config
import logging
import sys
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types

from filters import IsAdminFilter

sys.path.append("./censure")
from censure import Censor

censor_ru = Censor.get(lang="ru") # censor

def check_for_profanity(text):
    line_info = censor_ru.clean_line(text)
     

    _word = line_info[0][3] if line_info[1] else line_info[4][0] if line_info[2] else None

    return not _word is None, _word, line_info



logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
dp.filters_factory.bind(IsAdminFilter)

async def report_reminder():
    await asyncio.sleep(1) 
    while True:
        try:
            await bot.send_message(
            config.LOG_ID,
                "<b>❕ Не забывайте про команду !report</b> \n \n благодаря которой Вы можете обратить внимание администрации на нарушителей в чате. \n \n Спам данной командой карается перманентным баном.",
                parse_mode="HTML"
            )
            print("Message about !report sended")
        except Exception as e:
            print(f"Error by sending message {e}")
        await asyncio.sleep(14400) # 4 hours

async def start_reminder():
    await asyncio.sleep(1) 
    while True:
        try:
            await bot.send_message(
            config.LOG_ID,
                "<b>Working Log</b> \n \n Every 10 minutes.",
                parse_mode="HTML"
            )
            print("Message 'Every 10 minutes.' sended")
        except Exception as e:
            print(f"Error by sending message {e}")
        await asyncio.sleep(600) # 10 minutes

@dp.message_handler(commands=["бу"], commands_prefix="!/")
async def cmd_boo(message: types.Message):
    responses = [
        "Лучше принеси мне пивка",
        "Опять мешают работать!",
        "Ну и зачем ты это сказал?😤",
        "Так и до инфаркта можно довести!"
    ]

    reply = random.choice(responses)
    await message.reply(reply)
		
@dp.message_handler(chat_id=config.GROUP_ID, is_admin=True, commands=["ban"], commands_prefix="!/")
async def cmd_ban(message: types.Message):
	if not message.reply_to_message:
		await message.rseply("Эта команда должна быть ответом на сообщение!")
		return
	
	await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)

	await message.answer("Участник заблокирован.")

@dp.message_handler(commands=["report"], commands_prefix="!/")
async def cmd_report(message: types.Message):
    user_reports = [
        "Щя кто-то чекнет :3",
        "Жалоба отправлена на рассмотрение",
        "🚔 Служба Telegram уже в пути!"
    ]	

    admin_reports = [
         "Ты только что репортнул АДМИНА. Удачи.",
         "Хочешь бан? Так и запишем... 📝",
         "Репорт администратора зафиксирован. А ты смелый!",
         "Админов репортишь? Ай-ай-ай 😈",
         "Мы, конечно, передадим... но не обещаем, что выживешь."
    ]
    
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть ответом на сообщение!")
        return

    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

    reported_user = message.reply_to_message.from_user
    responses = user_reports

    try:
        chat_member = await message.bot.get_chat_member(message.chat.id, reported_user.id)
        if chat_member.status in ['administrator', 'creator']:
            responses = admin_reports
    except Exception as e:
        print(f"Error retrieving user data")

    reply = random.choice(responses)
    await message.reply(reply)

    log_message = (
        f"<b>[REPORT]</b>\n"
        f"🕒 <b>Time:</b> {current_time}\n"		
    )

    await bot.send_message(config.LOG_ID, log_message, parse_mode="HTML")

    return

# filter
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    comment = message.text
    check_result = check_for_profanity(comment)

    responses = [
        "Щас кому-то язык с мылом помою!",
        "В наше время так не выражались.",
        "Что за поколение, других слов не знаешь?",
    ]

    if check_result[0]:
        reply = random.choice(responses)
        await message.reply(reply)
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        log_message = (
            f"<b>[LOG]</b>\n"
            f"🕒 <b>Time:</b> {current_time}\n"
            f"👤 <b>User:</b> {message.from_user.full_name} (@{message.from_user.username})\n"
            f"💬 <b>Text:</b> \"{comment}\"\n"
			f"<b>RESULT:</b> Message deleted."
			
        )

        await bot.send_message(config.LOG_ID, log_message, parse_mode="HTML")
        await message.delete()

async def on_startup(dispatcher):
    asyncio.create_task(report_reminder())
    asyncio.create_task(start_reminder())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)