#!/bin/bash

# Вихід при помилці будь-якої команди
set -e

echo "🚀 Запускаємо Arbitrage Bot..."

# 1. Створення віртуального середовища, якщо його не існує
if [ ! -d "venv" ]; then
    echo "📦 Створюємо віртуальне середовище..."
    python3 -m venv venv
fi

# 2. Активація віртуального середовища
source venv/bin/activate

# 3. Оновлення pip та встановлення залежностей
echo "📥 Встановлюємо залежності..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Застосування міграцій бази даних
echo "🗃️ Оновлюємо базу даних..."
flask db upgrade

# 5. Запуск проєкту
echo "🌐 Запускаємо сервер..."
python run.py
