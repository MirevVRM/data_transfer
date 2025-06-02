# ========================================
# Файл: clear_data.py (обновлённый)
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: июнь 2025
# Назначение:
#   - RU: Очистка всех логов и данных
#   - EN: Clear all logs and data
# ========================================

import os
import glob
from datetime import datetime

# ========== Язык ==========
def choose_language():
    lang = input("Выберите язык / Choose language [Rus/Eng] (по умолчанию: Rus): ").strip().lower()
    return 'eng' if lang == 'eng' else 'rus'

LANG = choose_language()

TEXT = {
    'rus': {
        'title': "=== Очистка данных и логов ===",
        'confirm': "Удалить все файлы CSV и логов? (y/n): ",
        'cancelled': "Очистка отменена.",
        'cancelled_log': "Очистка отменена пользователем",
        'start': "Запрос на очистку",
        'deleted': "Удалён файл: {}",
        'not_found': "Файл не найден: {}",
        'done': "Очистка завершена"
    },
    'eng': {
        'title': "=== Data and Log Cleanup ===",
        'confirm': "Delete all CSV and log files? (y/n): ",
        'cancelled': "Cleanup cancelled.",
        'cancelled_log': "Cleanup cancelled by user",
        'start': "Cleanup initiated",
        'deleted': "File deleted: {}",
        'not_found': "File not found: {}",
        'done': "Cleanup completed"
    }
}

T = TEXT[LANG]
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

    # Одиночные файлы
    standalone_files = [
        "sent_data.csv",
        "received_data.csv",
        "encrypted_packet.bin",
        "sender_log.txt",
        "receiver_log.txt",
        "main_log.txt",
        "manage_log.txt"
    ]

    # CSV и логи в папках
    pattern_paths = [
        "data/sent/*.csv",
        "data/received/*.csv",
        "logs/*.txt"
    ]

    for file in standalone_files:
        if os.path.exists(file):
            os.remove(file)
            log_event(T['deleted'].format(file))
        else:
            log_event(T['not_found'].format(file))

    for pattern in pattern_paths:
        for path in glob.glob(pattern):
            try:
                os.remove(path)
                log_event(T['deleted'].format(path))
            except Exception:
                log_event(T['not_found'].format(path))

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
