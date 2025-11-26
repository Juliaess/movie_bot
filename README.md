# Movie Search Bot 🎬

## Описание проекта
***Movie Search Bot*** - это Telegram-бот для поиска информации о фильмах и сериалах.
Бот решает проблему быстрого доступа к актуальной информации о кинокартинах, их рейтингах, бюджете и других характеристиках.
Пользователи могут легко находить фильмы по различным критериям и просматривать историю своих запросов.

## Как пользоваться

### Команды бота

*default commands*:

- **/start** - начало работы с ботом, выводит приветственное сообщение и основное меню

- **/hello_world** - аналогична команде `/start`

- **/help** - Показывает список всех доступных команд с описанием

*custom commands*:

- **/movie_search** - Поиск фильма по названию

**Запрос с параметрами:**

```bash
GET https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=10&query=интерстеллар
```

**Пример ответа:**

```json
{
  "docs": [
    {
      "id": 535341,
      "name": "Интерстеллар",
      "year": 2014,
      "rating": {"kp": 8.6},
      "description": "Когда засуха приводит человечество к продовольственному кризису...",
      "genres": [{"name": "фантастика"}, {"name": "драma"}],
      "ageRating": 16,
      "poster": {"url": "https://example.com/poster.jpg"}
    }
  ]
}
```

- **/movie_by_rating** - Поиск фильмов по рейтингу

**Запрос с параметрами:**

```bash
GET https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&rating.kp=7-10
````

**Пример ответа:**

```json
{
  "docs": [
    {
      "id": 535341,
      "name": "Интерстеллар",
      "rating": {"kp": 8.6},
      "year": 2014,
      "description": "Описание фильма...",
      "genres": [{"name": "фантастика"}],
      "ageRating": 16,
      "poster": {"url": "https://example.com/poster.jpg"}
    }
  ]
}
```

- **/low_budget_movie** - Поиск фильмов с низким бюджетом

**Запрос с параметрами:**

```bash
GET https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&budget.value=1000-1000000&sortField=budget.value&sortType=1
```

**Пример ответа:**

```json
{
  "docs": [
    {
      "id": 12345,
      "name": "Независимый фильм",
      "budget": {"value": 500000},
      "rating": {"kp": 7.2},
      "year": 2023,
      "description": "Описание фильма...",
      "genres": [{"name": "драма"}],
      "ageRating": 16,
      "poster": {"url": "https://example.com/poster.jpg"}
    }
  ]
}
```

- **/high_budget_movie** - Поиск фильмов с высоким бюджетом

**Запрос с параметрами:**

```bash
GET https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&budget.value=100000000-500000000&sortField=budget.value&sortType=-1
```

**Пример ответа:**

```json
{
  "docs": [
    {
      "id": 67890,
      "name": "Блокбастер",
      "budget": {"value": 200000000},
      "rating": {"kp": 8.1},
      "year": 2024,
      "description": "Описание фильма...",
      "genres": [{"name": "фантастика"}],
      "ageRating": 12,
      "poster": {"url": "https://example.com/poster.jpg"}
    }
  ]
}
```

- **/history** - Просмотр истории поиска

Локальная команда, работает с базой данных проекта, не требует запросов к внешнему API.

## Использованные онлайн сервисы

**Кинопоиск API**

- **Базовый URL:** https://kinopoisk.dev/

- **Документация:** https://api.kinopoisk.dev/

- **Версия API:** v1.4

- **Лимиты:** 500 запросов в день на бесплатном тарифе

**Структура основных endpoints:**

**Поиск фильмов:**

```text
GET /v1.4/movie/search?query={название}&page={страница}&limit={лимит}
```

**Поиск с фильтрами:**

```text
GET /v1.4/movie?rating.kp={мин-макс}&year={год}&genres.name={жанр}
```

## Как запустить

### 1. Установка зависимостей

Убедитесь, в `requirements.txt` есть следующие пакеты:

- `pytelegrambotapi` - для работы с Telegram API

- `python-dotenv` - для загрузки переменных окружения

- `peewee` - ORM для работы с базой данных

- `requests` - для HTTP-запросов к API

- `loguru` - для логирования

- `psycopg2-binary` - PostgreSQL

Откройте терминал в папке проекта и выполните:

```bash
pip install -r requirements.txt
```
#### Настройка PostgreSQL

###### 1. Установка PostgreSQL
- **Windows**: [PostgreSQL Download](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

###### 2. Создание базы данных
```bash
# Подключитесь к PostgreSQL и введите пароль postgres
psql -U postgres

# Создайте базу данных
CREATE DATABASE movie_bot;

# Выйдите
\q
````

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=ваш_токен_бота_от_BotFather
KINOPOISK_API_KEY=ваш_ключ_от_Кинопоиск_API
```

### 3. Получение API ключей

**Telegram Bot Token:**

1. Напишите @BotFather в Telegram

2. Используйте команду /newbot

3. Следуйте инструкциям и получите токен

4. Добавьте токен в .env файл

**Кинопоиск API Key:**

1. Зарегистрируйтесь на https://kinopoisk.dev/

2. Получите API ключ из личного кабинета

3. Добавьте ключ в `.env` файл

### 4. Запуск бота

Выполните в терминале:

```bash
python main.py
```

Если все настроено правильно, вы увидите в терминале:

```text
🤖 Бот запущен!
Для остановки используйте Ctrl + C
```

### 5. Проверка работы

Перейдите в Telegram, найдите вашего бота по имени и отправьте команду `/start` для начала работы.