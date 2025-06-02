# ========================================
# Файл: autostart_receiver.py (обновлённый)
# Версия: июнь 2025
# ========================================

import csv
import os
import time
import serial
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Конфигурация ==========
UART_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
AES_KEY = "cat".ljust(16)[:16].encode()
RECEIVE_DURATION = 780  # 13 минут
DEBUG = False

# ========== Язык сообщений ==========
LANG = "rus"  # или "eng"

TEXT = {
    'rus': {
        'start': "=== UART-Приёмник (autostart_receiver.py) ===",
        'start_log': "Приём по UART запущен",
        'crc_fail': "CRC не совпадает — пакет отброшен",
        'decrypt_fail': "Ошибка расшифровки пакета",
        'format_error': "Неверный формат расшифрованных данных",
        'value_error': "Ошибка преобразования данных",
        'packet_saved': "Пакет ID {} сохранён",
        'user_stop': "Приём остановлен вручную",
        'finished': "Приём завершён",
        'done': "Готово.",
        'port_error': "Не удалось открыть порт {}: {}"
    },
    'eng': {
        'start': "=== UART Receiver (autostart_receiver.py) ===",
        'start_log': "UART reception started",
        'crc_fail': "CRC mismatch — packet dropped",
        'decrypt_fail': "Packet decryption failed",
        'format_error': "Invalid decrypted data format",
        'value_error': "Data conversion error",
        'packet_saved': "Packet ID {} saved",
        'user_stop': "Reception stopped manually",
        'finished': "Reception completed",
        'done': "Done.",
        'port_error': "Failed to open port {}: {}"
    }
}

T = TEXT[LANG]

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

# ========== Поиск следующего номера запуска ==========
def get_next_run_number(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    existing = [f for f in os.listdir(log_dir) if f.startswith("log_run_") and f.endswith(".txt")]
    numbers = []
    for f in existing:
        parts = f.replace("log_run_", "").replace(".txt", "")
        if parts.isdigit():
            numbers.append(int(parts))
    return max(numbers, default=0) + 1

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
    print(TEXT['start'])

    run_number = get_next_run_number()
    log_filename = f"logs/log_run_{run_number}.txt"
    csv_filename = f"data/received/received_run_{run_number}.csv"

    os.makedirs("data/received", exist_ok=True)

    try:
        uart = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        log_event(log_filename, TEXT['port_error'].format(UART_PORT, e))
        return

    log_event(log_filename, TEXT['start_log'])
    start_time = time.time()

    try:
        while time.time() - start_time < RECEIVE_DURATION:
            raw = uart.read(33)
            if not raw or len(raw) < 17:
                continue

            data, received_crc = raw[:-1], raw[-1]
            calculated_crc = crc8(data)
            crc_ok = (received_crc == calculated_crc)

            if not crc_ok:
                log_event(log_filename, TEXT['crc_fail'])
                continue

            decrypted = decrypt_message(data)
            if decrypted is None:
                log_event(log_filename, TEXT['decrypt_fail'])
                continue

            parts = decrypted.split(",")
            if len(parts) != 6:
                log_event(log_filename, TEXT['format_error'])
                continue

            try:
                packet_id = int(parts[0])
                payload = list(map(int, parts[1:]))
            except ValueError:
                log_event(log_filename, TEXT['value_error'])
                continue

            save_to_csv(csv_filename, packet_id, payload, crc_ok)
            log_event(log_filename, TEXT['packet_saved'].format(packet_id))

    except KeyboardInterrupt:
        log_event(log_filename, TEXT['user_stop'])
    finally:
        uart.close()
        log_event(log_filename, TEXT['finished'])
        os.system("sudo shutdown now")

if __name__ == '__main__':
    main()
