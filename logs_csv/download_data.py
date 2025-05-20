# ========================================
# Файл: download_data.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - RU: Загрузка CSV и лог-файлов с Raspberry Pi по SCP
#   - EN: Download CSV and log files from Raspberry Pi via SCP
# ========================================

import subprocess
from datetime import datetime
import os

# ========== Выбор языка ==========
def choose_language():
    lang = input("Выберите язык / Choose language [Rus/Eng] (по умолчанию: Rus): ").strip().lower()
    return 'eng' if lang == 'eng' else 'rus'

LANG = choose_language()

TEXT = {
    'rus': {
        'title': "=== Загрузка файлов с Raspberry Pi по SCP ===",
        'prompt': "Введите данные для подключения к Raspberry Pi:",
        'user': "Имя пользователя [по умолчанию: pi]: ",
        'host': "IP или имя Raspberry Pi [по умолчанию: raspberrypi.local]: ",
        'path': "Путь к файлам на Pi [по умолчанию: /home/pi/]: ",
        'connecting': "Подключение к {user}@{host}",
        'downloading': "Начинается загрузка файлов из {path}",
        'success': "Загружен: {file}",
        'fail': "Не удалось загрузить: {file}",
        'done': "Загрузка завершена"
    },
    'eng': {
        'title': "=== Downloading files from Raspberry Pi via SCP ===",
        'prompt': "Enter connection details for Raspberry Pi:",
        'user': "Username [default: pi]: ",
        'host': "IP or hostname [default: raspberrypi.local]: ",
        'path': "Path to files on Pi [default: /home/pi/]: ",
        'connecting': "Connecting to {user}@{host}",
        'downloading': "Starting download from {path}",
        'success': "Downloaded: {file}",
        'fail': "Failed to download: {file}",
        'done': "Download complete"
    }
}

T = TEXT[LANG]

# ========== Файлы для загрузки ==========
FILES = [
    "sent_data.csv",
    "received_data.csv",
    "sender_log.txt",
    "receiver_log.txt"
]

LOG_FILE = "download_log.txt"
DEST_FOLDER = "D:/logs_csv"

# ========== Логирование ==========
def log_event(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Запрос настроек ==========
def get_connection_info():
    print(T['prompt'])
    user = input(T['user']).strip() or "pi"
    host = input(T['host']).strip() or "raspberrypi.local"
    path = input(T['path']).strip() or "/home/pi/"
    return user, host, path

# ========== Загрузка ==========
def download_files(user, host, remote_path):
    os.makedirs(DEST_FOLDER, exist_ok=True)
    log_event(T['connecting'].format(user=user, host=host))
    log_event(T['downloading'].format(path=remote_path))

    for file in FILES:
        remote = f"{user}@{host}:{remote_path}/{file}"
        destination = os.path.join(DEST_FOLDER, file)
        try:
            subprocess.run(["scp", remote, destination], check=True)
            log_event(T['success'].format(file=file))
        except subprocess.CalledProcessError:
            log_event(T['fail'].format(file=file))

    log_event(T['done'])

# ========== Запуск ==========
if __name__ == "__main__":
    print(T['title'])
    user, host, path = get_connection_info()
    download_files(user, host, path)
