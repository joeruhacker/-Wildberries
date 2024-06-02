import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import time

# Настройки
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
WILDBERRIES_API_KEY = 'YOUR_WILDBERRIES_API_KEY'
WILDBERRIES_API_URL = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Ответы в зависимости от рейтинга
RESPONSES = {
    1: "Мы вам перезвоним.",
    2: "Мы заботимся о вас.",
    3: "Мы едем.",
    4: "Спасибо.",
    5: "Нормально."
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для автоматического ответа на отзывы.')

def check_feedbacks():
    headers = {'Authorization': WILDBERRIES_API_KEY}
    params = {
        'isAnswered': False,
        'take': 100,  # Количество необработанных отзывов для получения
        'skip': 0
    }
    
    response = requests.get(f'{WILDBERRIES_API_URL}/unanswered', headers=headers, params=params)
    feedbacks = response.json().get('data', [])

    for feedback in feedbacks:
        feedback_id = feedback['id']
        rating = feedback['productValuation']
        response_text = RESPONSES.get(rating, "Спасибо за ваш отзыв!")

        # Отправка ответа на отзыв
        answer_response(feedback_id, response_text)

def answer_response(feedback_id, text):
    headers = {'Authorization': WILDBERRIES_API_KEY}
    data = {
        'id': feedback_id,
        'answer': {'text': text}
    }
    response = requests.patch(f'{WILDBERRIES_API_URL}/answer', headers=headers, json=data)
    if response.status_code == 200:
        logger.info(f"Ответ на отзыв {feedback_id} успешно отправлен.")
    else:
        logger.error(f"Ошибка при отправке ответа на отзыв {feedback_id}: {response.text}")

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()

    while True:
        check_feedbacks()
        time.sleep(60)  # Проверка каждые 60 секунд

    updater.idle()

if __name__ == '__main__':
    main()
