# ========================================
# Файл: receiver.py (UART-версия) (ручной режим + язык + завершение)
# Автор: Snopkov D. I., Shimpf A.A.
# Версия: июнь 2025
# Назначение:
#   - RU: Приём зашифрованных пакетов с CRC8 по UART от E22-900T22S
#   - EN: Receiving AES-encrypted CRC8 packets via UART from E22-900T22S
#   - Расшифровка AES и сохранение в CSV
# ========================================

import csv
import os
import time
import serial
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Язык ==========
def choose_language():
    lang = input("Выберите язык / Choose language [Rus/Eng] (по умолчанию: Rus): ").strip().lower()
    return 'eng' if lang == 'eng' else 'rus'

LANG = choose_language()

TEXTS = {
    'rus': {
        'start': "=== UART-Приёмник (receiver.py) ===",
        'run_number': "Введите номер запуска: ",
        'distance': "Введите дистанцию (м): ",
        'start_log': "Приём по UART запущен",
        'crc_fail': "CRC не совпадает — пакет отброшен",
        'decrypt_fail': "Ошибка расшифровки пакета",
        'format_error': "Неверный формат расшифрованных данных",
        'value_error': "Ошибка преобразования данных",
        'packet_saved': "Пакет ID {} сохранён",
        'user_stop': "Приём остановлен вручную",
        'finished': "Приём завершён",
        'done': "Готово.",
        'port_error': "Не удалось открыть порт {}: {}",
        'exit_choice': "Завершить только скрипт или выключить контроллер? [script/shutdown]: ",
        'shutdown': "Завершение работы контроллера...",
        'exit_script': "Завершение работы скрипта..."
    },
    'eng': {
        'start': "=== UART Receiver (receiver.py) ===",
        'run_number': "Enter run number: ",
        'distance': "Enter distance (m): ",
        'start_log': "UART reception started",
        'crc_fail': "CRC mismatch — packet dropped",
        'decrypt_fail': "Packet decryption failed",
        'format_error': "Invalid decrypted data format",
        'value_error': "Data conversion error",
        'packet_saved': "Packet ID {} saved",
        'user_stop': "Reception stopped manually",
        'finished': "Reception completed",
        'done': "Done.",
        'port_error': "Failed to open port {}: {}",
        'exit_choice': "Exit script only or shut down controller? [script/shutdown]: ",
        'shutdown': "Shutting down controller...",
        'exit_script': "Exiting script..."
    }
}

T = TEXTS[LANG]

# ========== Конфигурация ==========
UART_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
AES_KEY = "cat".ljust(16)[:16].encode()
DEBUG = False

# ========== CRC8 ==========
def crc8(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if crc & 0x80 else crc << 1
            crc &= 0xFF
    return crc

# ========== AES Расшифровка ==========
def decrypt_message(ciphertext):
    try:
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode()
    except Exception:
        return None

# ========== Логирование ==========
def log_event(logfile, text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    if DEBUG:
        print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Сохранение в CSV ==========
def save_to_csv(csvfile, packet_id, data, crc_ok):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity',
              'density', 'concentration', 'crc_ok']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data + [crc_ok]
    file_exists = os.path.exists(csvfile)
    with open(csvfile, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

# ========== Основной цикл ==========
def main():
    print(T['start'])

    run_number = input(T['run_number']).strip()
    distance = input(T['distance']).strip()

    log_filename = f"logs/log_run_{run_number}_{distance}m.txt"
    csv_filename = f"data/received/received_run_{run_number}_{distance}m.csv"
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/received", exist_ok=True)

    try:
        uart = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        log_event(log_filename, T['port_error'].format(UART_PORT, e))
        return

    log_event(log_filename, T['start_log'])

    try:
        while True:
            raw = uart.read(33)
            if not raw or len(raw) < 17:
                continue

            data, received_crc = raw[:-1], raw[-1]
            calculated_crc = crc8(data)
            crc_ok = (received_crc == calculated_crc)

            if not crc_ok:
                log_event(log_filename, T['crc_fail'])
                continue

            decrypted = decrypt_message(data)
            if decrypted is None:
                log_event(log_filename, T['decrypt_fail'])
                continue

            parts = decrypted.split(",")
            if len(parts) != 6:
                log_event(log_filename, T['format_error'])
                continue

            try:
                packet_id = int(parts[0])
                payload = list(map(int, parts[1:]))
            except ValueError:
                log_event(log_filename, T['value_error'])
                continue

            save_to_csv(csv_filename, packet_id, payload, crc_ok)
            log_event(log_filename, T['packet_saved'].format(packet_id))

    except KeyboardInterrupt:
        log_event(log_filename, T['user_stop'])
    finally:
        uart.close()
        log_event(log_filename, T['finished'])
        print(T['done'])

        action = input(T['exit_choice']).strip().lower()
        if action == "shutdown":
            print(T['shutdown'])
            os.system("sudo shutdown now")
        else:
            print(T['exit_script'])

if __name__ == '__main__':
    main()

