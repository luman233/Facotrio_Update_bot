import os
import requests
import re
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://factorio.com/download/sha256sums/"
HASH_FILE = "last_hash.txt"
PIN_FILE = "pin_id.txt"  # Здесь будем хранить ID закреплённого сообщения

def fetch_sha256():
    response = requests.get(URL)
    response.raise_for_status()
    return response.text

def extract_version(text):
    match = re.search(r'Setup_Factorio_(\d+\.\d+\.\d+)\.exe\.zip', text)
    return match.group(1) if match else None

def load_last_hash():
    if not os.path.exists(HASH_FILE):
        return None
    with open(HASH_FILE, 'r') as f:
        return f.read().strip()

def save_current_hash(data):
    with open(HASH_FILE, 'w') as f:
        f.write(data)

def load_pin_id():
    if not os.path.exists(PIN_FILE):
        return None
    with open(PIN_FILE, 'r') as f:
        return int(f.read().strip())

def save_pin_id(message_id):
    with open(PIN_FILE, 'w') as f:
        f.write(str(message_id))

def clear_pin_id():
    if os.path.exists(PIN_FILE):
        os.remove(PIN_FILE)

def notify_and_pin(bot, version):
    version_escaped = version.replace('.', '\\.')
    message = (
        f"*🚀 Вышла новая версия Факторио\\!*\n"
        f"Ссылка на обновление: [factorio\\.com](https://factorio.com/download)\n"
        f"Версия: *{version_escaped}*"
    )

    msg = bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode="MarkdownV2",
        disable_notification=True  # Без звука
    )

    bot.pin_chat_message(
        chat_id=CHAT_ID,
        message_id=msg.message_id,
        disable_notification=True
    )

    save_pin_id(msg.message_id)

def main():
    bot = Bot(token=TELEGRAM_TOKEN)

    pin_id = load_pin_id()
    if pin_id:
        try:
            bot.unpin_chat_message(chat_id=CHAT_ID, message_id=pin_id)
            clear_pin_id()
        except Exception as e:
            print(f"⚠️ Не удалось открепить сообщение: {e}")

    current = fetch_sha256()
    last = load_last_hash()

    if last is None:
        print("Файл last_hash.txt не найден. Создаю и выхожу.")
        save_current_hash(current)
        return

    if current != last:
        version = extract_version(current)
        if version:
            notify_and_pin(bot, version)
        save_current_hash(current)
    else:
        print("Обновлений нет.")

if __name__ == "__main__":
    main()
