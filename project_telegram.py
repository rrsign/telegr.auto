import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from telegram.ext import Updater, CommandHandler
import config

# Функция для парсинга новостного сайта
def parse_news_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')

    news = []
    for article in articles:
        title = article.find('h2').text
        summary = article.find('p').text
        news.append({'title': title, 'summary': summary})

    return news

# Функция для обработки текста
def process_text(text):
    # Перевод текста
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-en")
    translated = translator(text, max_length=512)[0]['translation_text']

    # Определение темы
    classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
    sentiment = classifier(translated)[0]['label']

    # Генерация ключевых фраз
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(translated, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

    return f"Перевод: {translated}\\nТема: {sentiment}\\nКлючевые моменты: {summary}"

# Функция для отправки сообщения в Telegram
def send_to_telegram(update, context):
    news = parse_news_site('<https://example.com/news>')
    for item in news:
        processed = process_text(item['summary'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=processed)

# Настройка бота
updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('news', send_to_telegram))

updater.start_polling()
updater.idle()

