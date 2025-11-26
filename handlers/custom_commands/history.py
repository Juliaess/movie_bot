import json
import datetime
from typing import List
from loader import bot
from telebot.types import Message, CallbackQuery
from database.models import User, SearchHistory
from keyboards.inline.history import history_keyboard
from keyboards.inline.pagination import pagination_keyboard
from utils.shared import user_states_manager
from loguru import logger

HISTORY_PER_PAGE = 5


@bot.message_handler(commands=['history'])
def handle_history(message: Message):
    """Обработчик команды истории"""
    try:
        user = User.get_or_create(
            user_id=message.from_user.id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )[0]

        history_count = SearchHistory.select().where(SearchHistory.user == user).count()
        if history_count == 0:
            bot.send_message(message.chat.id, "📝 <b>История запросов</b>\n\nПока пусто 🗨️", parse_mode='HTML')
            return
        bot.send_message(message.chat.id, "📚 <b>История ваших запросов</b>\n\nВыберите период для просмотра:",
                         parse_mode='HTML', reply_markup=history_keyboard())

    except Exception as e:
        logger.error(f"Error in handle_history: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при получении истории")


@bot.callback_query_handler(func=lambda call: call.data in ['history_today', 'history_week', 'history_all'])
def handle_history_period(call: CallbackQuery):
    """Обработка выбора периода истории"""
    try:
        user_id = call.from_user.id
        user = User.get(User.user_id == user_id)
        period = call.data.split('_')[1]

        now = datetime.datetime.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_text = "сегодня"
        elif period == 'week':
            start_date = now - datetime.timedelta(days=7)
            period_text = "за неделю"
        else:
            start_date = None
            period_text = "за все время"

        query = SearchHistory.select().where(SearchHistory.user == user)
        if start_date:
            query = query.where(SearchHistory.created_at >= start_date)

        history_records = list(query.order_by(SearchHistory.created_at.desc()))
        if not history_records:
            bot.edit_message_text(f"📝 <b>История запросов {period_text}</b>\n\nЗа выбранный период запросов не найдено.",
                                  call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return

        user_states_manager.set_state_with_data(user_id, 'history', 'viewing', {
            'records': history_records, 'period': period})
        show_history_page(call, history_records, period, 1)

    except Exception as e:
        logger.error(f"Error in handle_history_period: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при загрузке истории")


def show_history_page(call: CallbackQuery, history_records: List, period: str, page: int):
    """Показывает страницу истории"""
    try:
        total_records = len(history_records)
        total_pages = (total_records + HISTORY_PER_PAGE - 1) // HISTORY_PER_PAGE
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * HISTORY_PER_PAGE
        page_records = history_records[start_idx:start_idx + HISTORY_PER_PAGE]

        period_texts = {'today': 'сегодня', 'week': 'за неделю', 'all': 'за все время'}
        period_text = period_texts.get(period, 'за все время')

        message_text = (f"📚 <b>История запросов {period_text}</b>\n\n"
                        f"Страница {page} из {total_pages}\n"
                        f"Всего записей: {total_records}\n\n")

        for i, record in enumerate(page_records, start_idx + 1):
            try:
                movie_data = json.loads(record.movie_data)
                title = movie_data.get('name', 'Неизвестно')
                year = movie_data.get('year', '')
                rating = movie_data.get('rating', {}).get('kp', 'Н/Д')

                message_text += (f"<b>{i}.</b> {record.command}: <code>{record.query}</code>\n"
                                f"🎬 <b>{title}</b> ({year}) - ⭐ {rating}/10\n"
                                f"📅 {record.created_at.strftime('%d.%m.%Y %H:%M')}\n\n")

            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Error parsing movie data: {e}")
                message_text += (f"<b>{i}.</b> {record.command}: {record.query}\n"
                                f"📅 {record.created_at.strftime('%d.%m.%Y %H:%M')}\n\n")

        keyboard = pagination_keyboard(page, total_pages, f"history_{period}")

        try:
            bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                                  reply_markup=keyboard, parse_mode='HTML')
        except Exception as e:
            logger.warning(f"Could not edit message, sending new: {e}")
            bot.send_message( call.message.chat.id, message_text, reply_markup=keyboard, parse_mode='HTML')
        bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error in show_history_page: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при отображении истории")


@bot.callback_query_handler(func=lambda call: call.data.startswith('history_') and any(char.isdigit() for char in call.data))
def handle_history_pagination(call: CallbackQuery):
    """Обработка пагинации истории"""
    try:
        parts = call.data.split('_')
        period = parts[1]
        page = int(parts[2])

        user_id = call.from_user.id
        user_state = user_states_manager.get_state_data(user_id, 'history')

        if not user_state or 'records' not in user_state:
            bot.answer_callback_query(call.id, "❌ Данные истории устарели")
            return

        show_history_page(call, user_state['records'], period, page)

    except Exception as e:
        logger.error(f"Error in handle_history_pagination: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка пагинации")


@bot.callback_query_handler(func=lambda call: call.data == 'current_page')
def handle_current_page(call: CallbackQuery):
    """Обработка нажатия на текущую страницу (ничего не делаем)"""
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'history_periods')
def handle_back_to_periods(call: CallbackQuery):
    """Возврат к выбору периода истории"""
    try:
        user_id = call.from_user.id
        user_states_manager.clear_state(user_id, 'history')

        bot.edit_message_text("📚 <b>История ваших запросов</b>\n\nВыберите период для просмотра:",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=history_keyboard(), parse_mode='HTML')
        bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error in handle_back_to_periods: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
