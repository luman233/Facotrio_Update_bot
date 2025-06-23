import os
import re
import requests
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://factorio.com/download/sha256sums/"
HASH_FILE = "last_hash.txt"
PIN_FILE = "last_pin.txt"


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


def load_last_pin():
    if not os.path.exists(PIN_FILE):
        return None
    with open(PIN_FILE, 'r') as f:
        return f.read().strip()


def save_last_pin(message_id):
    with open(PIN_FILE, 'w') as f:
        f.write(str(message_id))


def clear_last_pin():
    if os.path.exists(PIN_FILE):
        os.remove(PIN_FILE)


async def notify(bot: Bot, version):
    version_escaped = version.replace('.', '\\.')
    message = (
        f"*🚀 Вышла новая версия Факторио\\!*\n"
        f"Ссылка на обновление: [factorio\\.com](https://factorio.com/download)\n"
        f"Версия: *{version_escaped}*"
    )

    msg = await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_notification=True
    )

    await bot.pin_chat_message(chat_id=CHAT_ID, message_id=msg.message_id, disable_notification=True)
    save_last_pin(msg.message_id)


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)

    # Открепить старое сообщение, если есть
    last_pin_id = load_last_pin()
    if last_pin_id:
        try:
            await bot.unpin_chat_message(chat_id=CHAT_ID, message_id=int(last_pin_id))
            print("Откреплено предыдущее сообщение.")
        except Exception as e:
            print(f"Ошибка при откреплении: {e}")
        clear_last_pin()

    # Проверка обновлений
    current = fetch_sha256()
    last = load_last_hash()

    if last is None:
        print("Первый запуск. Сохраняю хеш и выхожу.")
        save_current_hash(current)
        return

    if current != last:
        version = extract_version(current)
        if version:
            await notify(bot, version)
        save_current_hash(current)
    else:
        print("Обновлений нет.")


if __name__ == "__main__":
    asyncio.run(main())
