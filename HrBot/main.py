import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Contact, KeyboardButton, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from collections import defaultdict
from datetime import timedelta

id_accout_to_recieve_forms = '1389160692'


USERS_DATA = defaultdict(dict)
bot = Bot(token='6583302614:AAEsMidIKAfxkV4vKtR2a2mNulGOKIPeiUo')
# Enable logging
logging.basicConfig(
    format="| %(asctime)s | %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

NAME, AGE, CITY, INTEREST, PHONE = range(5)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.chat.id
    logger.info("User @%s start conversation.", update.message.chat.username)
    if user == 6657907495:
        await update.message.reply_text('Леди Роуз\nВам не стоит заполнять форму с своего аккаунта\nДля теста воспользуйтесь другим аккаунтом')
        return ConversationHandler.END
    await update.message.reply_text(
        "Здравствуйте \n\n"
        "Напиишите /cancel что бы закончить диалог.\n\n"
        "Как менеджер может к вам обращаться?")

    USERS_DATA[user] = {}
    return NAME


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.chat.id
    USERS_DATA[user]['name'] = update.message.text
    await update.message.reply_text(f"{USERS_DATA[user]['name']}, сколько вам полных лет ?")
    return AGE


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.chat.id
    try:
        age = int(update.message.text)
        if age < 18 or age > 50:
            await update.message.reply_text(
                "Всего доброго", reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        USERS_DATA[user]['age'] = update.message.text

    except ValueError:
        await update.message.reply_text(f"{USERS_DATA[user]['name']}, впишите возраст корректно")
        return AGE

    reply_keyboard = [["Киев", "Другой город.."]]
    await update.message.reply_text(
        "Откуда вы ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,),)
    return CITY

# Если киев
async def interest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.chat.id
    USERS_DATA[user]['city'] = update.message.text
    if update.message.text == 'Да':
        USERS_DATA[user]['city'] = 'Иногородний'

    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Мы работаем против страны агрессора\nВам это интересно ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True),)

    return INTEREST

# человек не из киева
async def another_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
            "Рассматриваете ли вы переезд в Киев?\nМы предоставляем жилье для иногородних",
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True))



# окончание и отправка Лере на акк
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[KeyboardButton("Отправить номер телефона", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Оставьте свой номер телефона что бы с вами связался менеджер:', reply_markup=reply_markup)

    return PHONE

# окончание и отправка Лере на акк
async def end_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.chat.id
    tg = update.message.chat.username
    name = USERS_DATA[user]['name']
    age = USERS_DATA[user]['age']
    city = USERS_DATA[user]['city']
    phone = update.message.contact.phone_number
    date = update.message.date + timedelta(hours=2)
    text = f'''
| Телеграм: @{tg}
| Имя: {name}
| Возраст: {age}
| Город: {city}
| Номер телефона: {phone}
| Дата заявки: {date.strftime("%A, %d %B %Y %H:%M:%S")}'''
    await bot.send_message(chat_id=id_accout_to_recieve_forms, text=text)

    await update.message.reply_text("Хорошего вам дня, скоро с вами свяжеться менеджер")
    return ConversationHandler.END



# отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "До свидания, удачи в поиске работы :)", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6583302614:AAEsMidIKAfxkV4vKtR2a2mNulGOKIPeiUo").build()
    application.add_error_handler(cancel)
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, age),
            ],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            CITY: [
                MessageHandler(filters.Regex("^Киев$") & ~filters.COMMAND, interest),
                MessageHandler(filters.Regex("^Другой город..$") & ~filters.COMMAND, another_city),
                MessageHandler(filters.Regex("^Да$") & ~filters.COMMAND, interest),
                MessageHandler(filters.Regex("^Нет$") & ~filters.COMMAND, cancel),
            ],
            INTEREST: [
                MessageHandler(filters.Regex("^Да$") & ~filters.COMMAND, phone),
                MessageHandler(filters.Regex("^Нет$") & ~filters.COMMAND, cancel),],
            PHONE: [MessageHandler(filters.CONTACT & ~filters.COMMAND, end_conv)],

        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

