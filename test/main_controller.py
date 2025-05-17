# ========================================
# Файл: main_controller.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - Управление запуском sender_test.py и receiver_test.py
#   - Очистка файлов данных и логов
#   - Логирование событий в main_log.txt
# ========================================

import os
import subprocess
import sys
from datetime import datetime

# ========== Настройки ==========
FILES_TO_DELETE = [
    "sent_data.csv",
    "received_data.csv",
    "encrypted_packet.bin",
    "sender_log.txt",
    "receiver_log.txt",
    "main_log.txt"
]

MAIN_LOG_FILE = "main_log.txt"
PYTHON = sys.executable  # Использовать тот же интерпретатор, что и для main_controller.py

# ========== Логирование ==========
def log_event(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(MAIN_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Действия ==========
def run_sender():
    log_event("Запуск sender_test.py")
    subprocess.run([PYTHON, "sender_test.py"], check=True)

def run_receiver():
    log_event("Запуск receiver_test.py")
    subprocess.run([PYTHON, "receiver_test.py"], check=True)

def clear_files():
    log_event("Очистка файлов запрошена")
    for file in FILES_TO_DELETE:
        if os.path.exists(file):
            os.remove(file)
            log_event(f"Удалён файл: {file}")
        else:
            log_event(f"Файл не найден: {file}")
    log_event("Очистка завершена")

# ========== Меню ==========
def main():
    log_event("Программа main_controller запущена")
    while True:
        print("\n========== МЕНЮ ==========")
        print("1. Отправить и принять пакет")
        print("2. Очистить все файлы")
        print("3. Выйти")
        choice = input("Выберите действие (1-3): ").strip()

        if choice == "1":
            run_sender()
            run_receiver()
        elif choice == "2":
            confirm = input("Точно очистить все файлы? (y/n): ").strip().lower()
            if confirm == "y":
                clear_files()
            else:
                print("Очистка отменена.")
                log_event("Очистка отменена пользователем")
        elif choice == "3":
            print("Выход.")
            log_event("Выход из программы")
            break
        else:
            print("Неверный выбор. Введите 1, 2 или 3.")
            log_event("Введён неверный пункт меню")

if __name__ == "__main__":
    main()
