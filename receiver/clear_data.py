# ========================================
# Файл: clear_data.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - Очистка локальных файлов данных и логов
#   - Логирование действий удаления
# ========================================

import os
from datetime import datetime

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
    log_event("Запрос на очистку файлов")
    for file in FILES_TO_DELETE:
        if os.path.exists(file):
            os.remove(file)
            log_event(f"Удалён файл: {file}")
        else:
            log_event(f"Файл не найден: {file}")
    log_event("Очистка завершена")

# ========== Запуск ==========
def main():
    print("\n=== Очистка данных ===")
    confirm = input("Удалить все перечисленные файлы? (y/n): ").strip().lower()
    if confirm == "y":
        clear_files()
    else:
        print("Очистка отменена.")
        log_event("Очистка отменена пользователем")

if __name__ == "__main__":
    main()
