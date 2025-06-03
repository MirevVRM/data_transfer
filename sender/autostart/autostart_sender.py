# ========================================
# Файл: autostart_sender.py (автозапуск + логика запуска)
# Версия: июнь 2025
# ========================================

import csv
import random
import time
import serial
import os
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ========== Конфигурация ==========
DEBUG = False

CONFIG = {
    "LANG": "rus",
    "DELAY_BEFORE_START": 5,
    "DURATION": 150,
    "INTERVAL": 15,
    "UART_PORT": "/dev/ttyUSB0",
    "BAUDRATE": 9600,
    "AES_KEY": "cat"
}

TEXT = {
    'rus': {
        'start': "=== UART-Передатчик (autostart_sender.py) ===",
        'wait': "Ожидание {} сек перед запуском...",
        'port_error': "Не удалось открыть порт {}: {}",
        'start_log': "Старт передачи данных через UART",
        'param': "Параметры:",
        'packet_built': "Сформирован пакет ID {}: {}",
        'sent': "Пакет отправлен.",
        'sent_log': "Отправлен пакет ID {}",
        'send_error': "Ошибка при отправке пакета ID {}: {}",
        'done': "Готово.",
        'finished': "Завершено: передача окончена",
        'user_stop': "Передача остановлена пользователем",
        'shutdown': "Завершение работы контроллера..."
    },
    'eng': {
        'start': "=== UART Transmitter (autostart_sender.py) ===",
        'wait': "Waiting {} sec before start...",
        'port_error': "Failed to open port {}: {}",
        'start_log': "Starting data transmission over UART",
        'param': "Parameters:",
        'packet_built': "Packet ID {} generated: {}",
        'sent': "Packet sent.",
        'sent_log': "Packet ID {} sent",
        'send_error': "Failed to send packet ID {}: {}",
        'done': "Done.",
        'finished': "Completed: transmission finished",
        'user_stop': "Transmission interrupted by user",
        'shutdown': "Shutting down controller..."
    }
}

T = TEXT[CONFIG["LANG"]]

# ========== Подготовка директорий и счётчика ==========
def get_next_run_number(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    existing = [f for f in os.listdir(log_dir) if f.startswith("log_run_") and f.endswith(".txt")]
    numbers = []
    for f in existing:
        parts = f.replace("log_run_", "").replace(".txt", "")
        if parts.isdigit():
            numbers.append(int(parts))
    return max(numbers, default=0) + 1

# ========== Логирование ==========
def log_event(logfile, text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    if DEBUG:
        print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Генерация параметров ==========
def generate_parameters():
    return [
        random.randint(20, 30),
        random.randint(980, 1020),
        random.randint(30, 80),
        random.randint(1, 5),
        random.randint(50, 150)
    ]

# ========== Сохранение в CSV ==========
def save_to_csv(csvfile, packet_id, data):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity', 'density', 'concentration']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data
    file_exists = os.path.exists(csvfile)
    with open(csvfile, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

# ========== Шифрование AES ==========
def encrypt_message(message, key_str):
    key = key_str.ljust(16)[:16].encode()
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(message.encode(), AES.block_size))

# ========== CRC8 ==========
def crc8(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if crc & 0x80 else crc << 1
            crc &= 0xFF
    return crc

# ========== Основной цикл ==========
def main():
    print(T['start'])

    run_number = get_next_run_number()
    log_filename = f"logs/log_run_{run_number}.txt"
    csv_filename = f"data/sent_run_{run_number}.csv"

    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    if CONFIG["DELAY_BEFORE_START"] > 0:
        log_event(log_filename, T['wait'].format(CONFIG["DELAY_BEFORE_START"]))
        time.sleep(CONFIG["DELAY_BEFORE_START"])

    try:
        uart = serial.Serial(
            port=CONFIG["UART_PORT"],
            baudrate=CONFIG["BAUDRATE"],
            timeout=1
        )
    except Exception as e:
        log_event(log_filename, T['port_error'].format(CONFIG["UART_PORT"], e))
        return

    log_event(log_filename, T['start_log'])
    start_time = time.time()

    try:
        while time.time() - start_time < CONFIG["DURATION"]:
            packet_id = int(time.time())
            params = generate_parameters()

            if DEBUG:
                print(T['param'], params)

            log_event(log_filename, T['packet_built'].format(packet_id, params))
            save_to_csv(csv_filename, packet_id, params)

            message = f"{packet_id}," + ",".join(map(str, params))
            encrypted = encrypt_message(message, CONFIG["AES_KEY"])
            crc = crc8(encrypted)
            full_packet = encrypted + bytes([crc])

            try:
                uart.write(full_packet)
                if DEBUG:
                    print(T['sent'])
                log_event(log_filename, T['sent_log'].format(packet_id))
            except Exception as e:
                log_event(log_filename, T['send_error'].format(packet_id, e))

            time.sleep(CONFIG["INTERVAL"])

        log_event(log_filename, T['finished'])
        if DEBUG:
            print(T['done'])

    except KeyboardInterrupt:
        log_event(log_filename, T['user_stop'])

    finally:
        uart.close()
        log_event(log_filename, T['shutdown'])
        os.system("sudo shutdown now")

if __name__ == '__main__':
    main()
