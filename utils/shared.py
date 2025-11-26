import time
from loguru import logger
from services.message import MessageFormatter


class UserStatesManager:
    def __init__(self):
        self.states = {}

    def set_state(self, user_id, command, step):
        if user_id not in self.states:
            self.states[user_id] = {}
        if command not in self.states[user_id]:
            self.states[user_id][command] = {}
        self.states[user_id][command]['step'] = step
        self.states[user_id][command]['timestamp'] = time.time()

    def set_state_with_data(self, user_id, command, step, data=None):
        if user_id not in self.states:
            self.states[user_id] = {}
        self.states[user_id][command] = {'step': step, 'timestamp': time.time()}
        if data:
            self.states[user_id][command].update(data)

    def get_state(self, user_id, command):
        user_data = self.states.get(user_id, {})
        command_data = user_data.get(command, {})
        return command_data.get('step')

    def get_state_data(self, user_id, command):
        user_data = self.states.get(user_id, {})
        return user_data.get(command, {})

    def update_state(self, user_id, command, updates):
        if user_id in self.states and command in self.states[user_id]:
            self.states[user_id][command].update(updates)

    def clear_state(self, user_id, command):
        if user_id in self.states and command in self.states[user_id]:
            del self.states[user_id][command]

    def cleanup_old_states(self, max_age=3600):
        current_time = time.time()
        users_to_remove = []

        for user_id, commands in self.states.items():
            commands_to_remove = []
            for command, data in commands.items():
                if current_time - data.get('timestamp', 0) > max_age:
                    commands_to_remove.append(command)

            for command in commands_to_remove:
                del commands[command]

            if not commands:
                users_to_remove.append(user_id)

        for user_id in users_to_remove:
            del self.states[user_id]


def send_and_delete_search_message(bot, chat_id, text="🔎 Поиск результатов..."):
    """Отправляет и сразу удаляет сообщение о поиске"""
    search_message = bot.send_message(chat_id, text)
    bot.delete_message(chat_id, search_message.message_id)


def send_movie_with_poster(bot, chat_id, movie, movie_details=None):
    """Функция для отправки фильма с постером"""
    if movie_details:
        message_text = MessageFormatter.format_movie_info(movie_details)
        poster_url = movie_details.get('poster', {}).get('url')
    else:
        message_text = MessageFormatter.format_movie_info(movie)
        poster_url = movie.get('poster', {}).get('url')

    if poster_url:
        try:
            bot.send_photo(chat_id, poster_url, caption=message_text, parse_mode='HTML')
            return
        except Exception as e:
            logger.warning(f"Couldn't send photo: {e}")

    bot.send_message(chat_id, message_text, parse_mode='HTML')


user_states_manager = UserStatesManager()
