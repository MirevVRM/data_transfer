# ========================================
# Файл: download_data.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - Загрузка CSV и лог-файлов с Raspberry Pi по SCP
#   - Сохранение в папку D:/logs_csv и логирование процесса
# ========================================

import subprocess
from datetime import datetime
import os

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
    print("Введите данные для подключения к Raspberry Pi:")
    user = input("Имя пользователя [по умолчанию: pi]: ").strip() or "pi"
    host = input("IP или имя Raspberry Pi [по умолчанию: raspberrypi.local]: ").strip() or "raspberrypi.local"
    path = input("Путь к файлам на Pi [по умолчанию: /home/pi/]: ").strip() or "/home/pi/"
    return user, host, path

# ========== Загрузка ==========
def download_files(user, host, remote_path):
    os.makedirs(DEST_FOLDER, exist_ok=True)
    log_event(f"Подключение к {user}@{host}")
    log_event(f"Начинается загрузка файлов из {remote_path}")

    for file in FILES:
        remote = f"{user}@{host}:{remote_path}/{file}"
        destination = os.path.join(DEST_FOLDER, file)
        try:
            subprocess.run(["scp", remote, destination], check=True)
            log_event(f"Загружен: {file}")
        except subprocess.CalledProcessError:
            log_event(f"Не удалось загрузить: {file}")

    log_event("Загрузка завершена")

# ========== Запуск ==========
if __name__ == "__main__":
    print("=== Загрузка файлов с Raspberry Pi по SCP ===")
    user, host, path = get_connection_info()
    download_files(user, host, path)
