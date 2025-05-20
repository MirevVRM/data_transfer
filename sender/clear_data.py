# ========================================
# Файл: clear_data.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - RU: Очистка локальных файлов данных и логов
#   - EN: Clear local data and log files
# ========================================

import os
from datetime import datetime

# ========== Язык ==========
def choose_language():
    lang = input("Выберите язык / Choose language [Rus/Eng] (по умолчанию: Rus): ").strip().lower()
    return 'eng' if lang == 'eng' else 'rus'

LANG = choose_language()

TEXT = {
    'rus': {
        'title': "=== Очистка данных ===",
        'confirm': "Удалить все перечисленные файлы? (y/n): ",
        'cancelled': "Очистка отменена.",
        'cancelled_log': "Очистка отменена пользователем",
        'start': "Запрос на очистку файлов",
        'deleted': "Удалён файл: {}",
        'not_found': "Файл не найден: {}",
        'done': "Очистка завершена"
    },
    'eng': {
        'title': "=== Data Cleanup ===",
        'confirm': "Delete all listed files? (y/n): ",
        'cancelled': "Cleanup cancelled.",
        'cancelled_log': "Cleanup cancelled by user",
        'start': "Request to clear files",
        'deleted': "File deleted: {}",
        'not_found': "File not found: {}",
        'done': "Cleanup completed"
    }
}

T = TEXT[LANG]

FILES_TO_DELETE = [
    "sent_data.csv",
    "received_data.csv",
    "encrypted_packet.bin",
    "sender_log.txt",
    "receiver_log.txt",
    "main_log.txt",
    "manage_log.txt",
    "clear_log.txt"
]

LOG_FILE = "clear_log.txt"

# ========== Логирование ==========
def log_event(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Очистка ==========
def clear_files():
    log_event(T['start'])
    for file in FILES_TO_DELETE:
        if os.path.exists(file):
            os.remove(file)
            log_event(T['deleted'].format(file))
        else:
            log_event(T['not_found'].format(file))
    log_event(T['done'])

# ========== Запуск ==========
def main():
    print(f"\n{T['title']}")
    confirm = input(T['confirm']).strip().lower()
    if confirm == "y":
        clear_files()
    else:
        print(T['cancelled'])
        log_event(T['cancelled_log'])

if __name__ == "__main__":
    main()
