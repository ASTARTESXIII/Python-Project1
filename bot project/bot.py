import os
import nest_asyncio
import asyncio
from dotenv import load_dotenv  # Импортируем библиотеку для работы с .env
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Применение nest_asyncio для поддержки asyncio в текущем окружении
nest_asyncio.apply()

# Загружаем переменные окружения из файла .env
load_dotenv()

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я помогу тебе с анализом вакансий.")

# Функция для команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Используйте команду /start для начала.")

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Произошла ошибка: {context.error}")

# Основная функция запуска бота
async def main() -> None:
    # Получаем токен из переменных окружения
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        raise ValueError("Токен не найден! Убедитесь, что TELEGRAM_TOKEN установлен в файле .env.")

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Добавляем обработчики команд /start и /help
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())