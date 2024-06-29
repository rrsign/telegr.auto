import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot
from transformers import pipeline, MarianMTModel, MarianTokenizer
import asyncio

# Конфигурация
TELEGRAM_TOKEN = '7475279076:AAF8tUpp3SdqWglWVDJf5MFAFzuNb-SGCQ0'
CHANNEL_ID = '-1002248988846'
URL = 'https://habr.com/ru/news/822725/'

# Инициализация моделей
generator = pipeline('text-generation', model='gpt2')
model_name = 'Helsinki-NLP/opus-mt-ru-en'
translate_model = MarianMTModel.from_pretrained(model_name)
translate_tokenizer = MarianTokenizer.from_pretrained(model_name)

async def parse_content(session, url):
    async with session.get(url) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        title = soup.find('h1', class_='tm-article-snippet__title_h1').text.strip()
        first_paragraph = soup.find('div', class_='tm-article-body').find('p').text.strip()
        return title, first_paragraph

async def change_tone(text):
    result = generator(text, max_length=100, num_return_sequences=1)
    return result[0]['generated_text']

async def translate_text(text):
    inputs = translate_tokenizer.encode(text, return_tensors='pt')
    outputs = translate_model.generate(inputs, max_length=400, num_return_sequences=1)
    return translate_tokenizer.decode(outputs[0], skip_special_tokens=True)

async def add_key_phrases(text):
    return text + "\n\nКлючевые фразы: ..."

async def process_content(title, first_paragraph):
    title_task = asyncio.create_task(change_tone(title))
    paragraph_task = asyncio.create_task(translate_text(first_paragraph))
    title = await title_task
    first_paragraph = await paragraph_task
    return title, await add_key_phrases(first_paragraph)

async def main():
    async with aiohttp.ClientSession() as session:
        bot = Bot(token=TELEGRAM_TOKEN)
        title, first_paragraph = await parse_content(session, URL)
        title, first_paragraph = await process_content(title, first_paragraph)
        message = f"{title}\n\n{first_paragraph}"
        await bot.send_message(chat_id=CHANNEL_ID, text=message)

if __name__ == '__main__':
    asyncio.run(main())

