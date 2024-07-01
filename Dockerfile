# Используйте официальный образ Python
FROM python:3.9-slim

# Установите рабочую директорию
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создание и активация виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование файлов проекта
COPY requirements.txt .
COPY project_telegram.py .

# Установка зависимостей Python в виртуальное окружение
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["python", "project_telegram.py"]