from loader import bot


@bot.message_handler(func=lambda message: message.text.lower() in ['привет', 'здравствуйте', 'hi', 'hello'])
def greet_user(message):
    bot.reply_to(message, "😊 Привет! Рад тебя видеть! Что хочешь посмотреть сегодня? Я помогу тебе найти интересные фильмы.")
