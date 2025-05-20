# ========================================
# Файл: sender.py (UART-версия)
# Автор: Snopkov D. I., Shimpf A.A.
# Версия: май 2025
# Назначение:
#   - RU: Отправка телеметрических пакетов по UART-модулю E22-900T22S
#   - EN: Transmitting telemetry packets over UART module E22-900T22S
#   - Шифрование (AES-128) + CRC8
# ========================================

import csv
import random
import time
import serial
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
        'start': "=== UART-Передатчик (sender.py) ===",
        'input_prompt': "Ввод параметров скрипта (нажмите Enter для значения по умолчанию)",
        'delay': "Задержка перед запуском (сек): ",
        'duration': "Общая длительность работы (сек): ",
        'interval': "Интервал между отправками (сек): ",
        'input_error': "Ошибка ввода. Используются значения по умолчанию.",
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
        'interrupted': "Прервано пользователем.",
        'user_stop': "Передача остановлена пользователем"
    },
    'eng': {
        'start': "=== UART Transmitter (sender.py) ===",
        'input_prompt': "Enter script parameters (press Enter to use defaults)",
        'delay': "Delay before start (sec): ",
        'duration': "Total run time (sec): ",
        'interval': "Interval between transmissions (sec): ",
        'input_error': "Input error. Using default values.",
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
        'interrupted': "Interrupted by user.",
        'user_stop': "Transmission interrupted by user"
    }
}

T = TEXT[LANG]

# ========== Логирование ==========
def log_event(text, logfile):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Конфигурация ==========
def get_config():
    print(T['input_prompt'])
    try:
        delay = int(input(T['delay']) or 0)
        duration = int(input(T['duration']) or 90)
        interval = int(input(T['interval']) or 30)
    except ValueError:
        print(T['input_error'])
        delay = 0
        duration = 90
        interval = 30

    return {
        "delay": delay,
        "duration": duration,
        "interval": interval,
        "csv_filename": "sent_data.csv",
        "log_filename": "sender_log.txt",
        "aes_key": "cat",
        "uart_port": "/dev/ttyUSB0",
        "baudrate": 9600
    }

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
def save_to_csv(packet_id, data, filename):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity', 'density', 'concentration']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data
    file_exists = False
    try:
        with open(filename, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass
    with open(filename, 'a', newline='') as f:
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
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

# ========== Основной цикл ==========
def main():
    print(T['start'])
    config = get_config()

    if config["delay"] > 0:
        print(T['wait'].format(config["delay"]))
        time.sleep(config["delay"])

    try:
        uart = serial.Serial(
            port=config["uart_port"],
            baudrate=config["baudrate"],
            timeout=1
        )
    except Exception as e:
        print(T['port_error'].format(config["uart_port"], e))
        return

    log_event(T['start_log'], config["log_filename"])
    start_time = time.time()

    try:
        while time.time() - start_time < config["duration"]:
            packet_id = int(time.time())
            params = generate_parameters()

            print(T['param'], params)
            log_event(T['packet_built'].format(packet_id, params), config["log_filename"])

            save_to_csv(packet_id, params, config["csv_filename"])

            message = f"{packet_id}," + ",".join(map(str, params))
            encrypted = encrypt_message(message, config["aes_key"])
            crc = crc8(encrypted)
            full_packet = encrypted + bytes([crc])

            try:
                uart.write(full_packet)
                print(T['sent'])
                log_event(T['sent_log'].format(packet_id), config["log_filename"])
            except Exception as e:
                print(T['send_error'].format(packet_id, e))
                log_event(T['send_error'].format(packet_id, e), config["log_filename"])

            time.sleep(config["interval"])

        log_event(T['finished'], config["log_filename"])
        print(T['done'])

    except KeyboardInterrupt:
        print("\n" + T['interrupted'])
        log_event(T['user_stop'], config["log_filename"])
    finally:
        uart.close()

if __name__ == '__main__':
    main()
