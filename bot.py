import os
import requests
import re
from telegram import Bot
from telegram.constants import ParseMode

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://factorio.com/download/sha256sums/"
HASH_FILE = "last_hash.txt"
PIN_FILE = "last_pin.txt"


# === Получить содержимое sha256sums ===
def fetch_sha256():
    response = requests.get(URL)
    response.raise_for_status()
    return response.text


# === Извлечь версию, например: 2.0.57 ===
def extract_version(text):
    match = re.search(r'Setup_Factorio_(\d+\.\d+\.\d+)\.exe\.zip', text)
    return match.group(1) if match else None


# === Загрузить предыдущий хеш (если есть) ===
def load_last_hash():
    if not os.path.exists(HASH_FILE):
        return None
    with open(HASH_FILE, 'r') as f:
        return f.read().strip()


# === Сохранить текущий хеш ===
def save_current_hash(data):
    with open(HASH_FILE, 'w') as f:
        f.write(data)


# === Загрузить предыдущий закреплённый message_id ===
def load_last_pin():
    if not os.path.exists(PIN_FILE):
        return None
    with open(PIN_FILE, 'r') as f:
        return f.read().strip()


# === Сохранить новый закреплённый message_id ===
def save_last_pin(message_id):
    with open(PIN_FILE, 'w') as f:
        f.write(str(message_id))


# === Удалить файл с message_id (если был откреплён) ===
def clear_last_pin():
    if os.path.exists(PIN_FILE):
        os.remove(PIN_FILE)


# === Уведомить о новой версии и закрепить сообщение ===
def notify(version):
    bot = Bot(token=TELEGRAM_TOKEN)

    version_escaped = version.replace('.', '\\.')
    message = (
        f"*🚀 Вышла новая версия Факторио\\!*\n"
        f"Ссылка на обновление: [factorio\\.com](https://factorio.com/download)\n"
        f"Версия: *{version_escaped}*"
    )

    msg = bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_notification=True
    )

    # Закрепляем сообщение без уведомления
    bot.pin_chat_message(chat_id=CHAT_ID, message_id=msg.message_id, disable_notification=True)
    save_last_pin(msg.message_id)


# === Основная логика ===
def main():
    bot = Bot(token=TELEGRAM_TOKEN)

    # 1. Попытка открепить предыдущее закреплённое сообщение
    last_pin_id = load_last_pin()
    if last_pin_id:
        try:
            bot.unpin_chat_message(chat_id=CHAT_ID, message_id=int(last_pin_id))
            print("Открепил предыдущее сообщение.")
        except Exception as e:
            print(f"Не удалось открепить сообщение: {e}")
        clear_last_pin()

    # 2. Получение текущего и предыдущего хеша
    current = fetch_sha256()
    last = load_last_hash()

    if last is None:
        print("Файл last_hash.txt не найден. Создаю и выхожу.")
        save_current_hash(current)
        return

    # 3. Проверка на обновление
    if current != last:
        version = extract_version(current)
        if version:
            notify(version)
        save_current_hash(current)
    else:
        print("Обновлений нет.")


# === Точка входа ===
if __name__ == "__main__":
    main()
