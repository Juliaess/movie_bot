from loader import bot
import handlers.default_commands.start # noqa
import handlers.default_commands.help # noqa
import handlers.default_commands.greet # noqa
import handlers.custom_commands.movie_search # noqa
import handlers.custom_commands.movie_by_rating # noqa
import handlers.custom_commands.budget_movies # noqa
import handlers.custom_commands.history # noqa
from utils.set_bot_commands import set_default_commands
from database.db_connection import init_database

if __name__ == '__main__':
    print("🤖 Бот запущен!\nДля остановки используйте Ctrl + C")
    init_database()
    set_default_commands(bot)
    bot.infinity_polling()
