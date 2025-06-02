# ========================================
# Файл: download_data.py
# Авторы: Snopkov D. I., Shimpf A. A. (обновлён)
# Версия: июнь 2025
# Назначение: Скачивание всех логов и .csv с Raspberry Pi по SCP
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
        'title': "=== Загрузка всех логов и CSV с Raspberry Pi ===",
        'prompt': "Введите данные для подключения к Raspberry Pi:",
        'user': "Имя пользователя [по умолчанию: pi]: ",
        'host': "IP или имя Raspberry Pi [по умолчанию: raspberrypi.local]: ",
        'path': "Базовый путь на Pi [по умолчанию: /home/pi/]: ",
        'connecting': "Подключение к {user}@{host}",
        'downloading': "Загрузка папок logs/, data/ и data/received/ из {path}",
        'success': "Загружено: {file}",
        'fail': "Ошибка загрузки: {file}",
        'done': "Загрузка завершена"
    },
    'eng': {
        'title': "=== Downloading all logs and CSV from Raspberry Pi ===",
        'prompt': "Enter connection details for Raspberry Pi:",
        'user': "Username [default: pi]: ",
        'host': "IP or hostname [default: raspberrypi.local]: ",
        'path': "Base path on Pi [default: /home/pi/]: ",
        'connecting': "Connecting to {user}@{host}",
        'downloading': "Downloading folders logs/, data/, and data/received/ from {path}",
        'success': "Downloaded: {file}",
        'fail': "Failed to download: {file}",
        'done': "Download complete"
    }
}

T = TEXT[LANG]

LOG_FILE = "download_log.txt"
DEST_FOLDER = "D:/logs_csv"

# ========== Логирование ==========
def log_event(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Запрос подключения ==========
def get_connection_info():
    print(T['prompt'])
    user = input(T['user']).strip() or "pi"
    host = input(T['host']).strip() or "raspberrypi.local"
    path = input(T['path']).strip() or "/home/pi/"
    return user, host, path

# ========== Загрузка директорий ==========
def download_directory(user, host, remote_base, subdir):
    os.makedirs(os.path.join(DEST_FOLDER, subdir), exist_ok=True)
    remote = f"{user}@{host}:{remote_base}/{subdir}/*"
    local = os.path.join(DEST_FOLDER, subdir)
    try:
        subprocess.run(["scp", "-r", remote, local], check=True)
        log_event(T['success'].format(file=subdir))
    except subprocess.CalledProcessError:
        log_event(T['fail'].format(file=subdir))

# ========== Запуск ==========
if __name__ == "__main__":
    print(T['title'])
    user, host, base_path = get_connection_info()
    log_event(T['connecting'].format(user=user, host=host))
    log_event(T['downloading'].format(path=base_path))

    for folder in ["logs", "data", "data/received"]:
        download_directory(user, host, base_path, folder)

    log_event(T['done'])
