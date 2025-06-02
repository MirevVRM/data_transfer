# ========================================
# Файл: sender_controlled.py
# Автор: Snopkov D. I., Shimpf A.A.
# Версия: июнь 2025
# Назначение: Интерактивная отправка 250 пакетов с отметкой дистанции и номера запуска
# ========================================

import csv
import random
import time
import serial
import os
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ========== Выбор языка ==========
def choose_language():
    lang = input("Выберите язык / Choose language [Rus/Eng] (по умолчанию: Rus): ").strip().lower()
    return 'eng' if lang == 'eng' else 'rus'

LANG = choose_language()

TEXT = {
    'rus': {
        'start': "=== UART-Передатчик (sender_controlled.py) ===",
        'start_prompt': "\nНачать новый запуск? (y/n): ",
        'run_number': "Введите номер запуска: ",
        'distance': "Введите дистанцию (м): ",
        'shutdown': "Завершение работы...",
        'port_error': "Не удалось открыть порт {}: {}",
        'run_start': "Запуск №{} на дистанции {} м",
        'packet_sent': "Отправлен пакет ID {}",
        'packet_error': "Ошибка отправки ID {}: {}",
        'run_done': "Завершено: отправлено {} пакетов."
    },
    'eng': {
        'start': "=== UART Transmitter (sender_controlled.py) ===",
        'start_prompt': "\nStart new run? (y/n): ",
        'run_number': "Enter run number: ",
        'distance': "Enter distance (m): ",
        'shutdown': "Shutting down...",
        'port_error': "Failed to open port {}: {}",
        'run_start': "Run #{} at distance {} m",
        'packet_sent': "Packet ID {} sent",
        'packet_error': "Failed to send ID {}: {}",
        'run_done': "Completed: {} packets sent."
    }
}

T = TEXT[LANG]

# ========== Параметры UART и AES ==========
UART_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
AES_KEY = "cat".ljust(16)[:16].encode()
PACKET_COUNT = 250
SEND_INTERVAL = 3  # секунды

# ========== Генерация параметров ==========
def generate_parameters():
    return [
        random.randint(20, 30),
        random.randint(980, 1020),
        random.randint(30, 80),
        random.randint(1, 5),
        random.randint(50, 150)
    ]

# ========== CRC8 ==========
def crc8(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

# ========== AES Шифрование ==========
def encrypt_message(message):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.encrypt(pad(message.encode(), AES.block_size))

# ========== Логирование ==========
def log_event(logfile, text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Сохранение CSV ==========
def save_csv(csvfile, packet_id, params, run_number, distance):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity', 'density', 'concentration', 'run_number', 'distance_m']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + params + [run_number, distance]
    file_exists = os.path.exists(csvfile)
    with open(csvfile, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

# ========== Основной цикл ==========
def main():
    print(T['start'])
    try:
        uart = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        print(T['port_error'].format(UART_PORT, e))
        return

    while True:
        choice = input(T['start_prompt']).strip().lower()
        if choice != 'y':
            print(T['shutdown'])
            os.system("sudo shutdown now")
            break

        run_number = input(T['run_number']).strip()
        distance = input(T['distance']).strip()

        log_filename = f"logs/log_run_{run_number}_{distance}m.txt"
        csv_filename = f"data/sent_run_{run_number}_{distance}m.csv"

        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

        log_event(log_filename, T['run_start'].format(run_number, distance))

        for _ in range(PACKET_COUNT):
            packet_id = int(time.time())
            params = generate_parameters()
            message = f"{packet_id}," + ",".join(map(str, params))
            encrypted = encrypt_message(message)
            crc = crc8(encrypted)
            full_packet = encrypted + bytes([crc])

            try:
                uart.write(full_packet)
                log_event(log_filename, T['packet_sent'].format(packet_id))
                save_csv(csv_filename, packet_id, params, run_number, distance)
            except Exception as e:
                log_event(log_filename, T['packet_error'].format(packet_id, e))

            time.sleep(SEND_INTERVAL)

        log_event(log_filename, T['run_done'].format(PACKET_COUNT))

if __name__ == '__main__':
    main()
