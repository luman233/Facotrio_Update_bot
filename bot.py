import os
import requests
import re
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://factorio.com/download/sha256sums/"
HASH_FILE = "last_hash.txt"


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


def notify(version):
    bot = Bot(token=TELEGRAM_TOKEN)
    message = (
        f"🚀 Вышла новая версия Факторио!\n"
        f"Ссылка на обновление: https://factorio.com/download\n"
        f"Версия: {version}"
    )
    bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current = fetch_sha256()
    last = load_last_hash()

    if current != last:
        version = extract_version(current)
        if version:
            notify(version)
        save_current_hash(current)
    else:
        print("Обновлений нет.")


if __name__ == "__main__":
    main()
