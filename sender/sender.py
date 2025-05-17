# ========================================
# Файл: sender.py (UART-версия)
# Автор: Snopkov D. I., Shimpf A.A.
# Версия: май 2025
# Назначение:
#   - Отправка телеметрических пакетов по UART-модулю E22-900T22S
#   - Шифрование (AES-128) + CRC8
# ========================================

import csv
import random
import time
import serial
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ========== Логирование ==========
def log_event(text, logfile):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Конфигурация ==========
def get_config():
    print("Ввод параметров скрипта (нажмите Enter для значения по умолчанию)")
    try:
        delay = int(input("Задержка перед запуском (сек): ") or 0)
        duration = int(input("Общая длительность работы (сек): ") or 90)
        interval = int(input("Интервал между отправками (сек): ") or 30)
    except ValueError:
        print("Ошибка ввода. Используются значения по умолчанию.")
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
    config = get_config()

    if config["delay"] > 0:
        print(f"Ожидание {config['delay']} сек перед запуском...")
        time.sleep(config["delay"])

    try:
        uart = serial.Serial(
            port=config["uart_port"],
            baudrate=config["baudrate"],
            timeout=1
        )
    except Exception as e:
        print(f"Не удалось открыть порт {config['uart_port']}: {e}")
        return

    log_event("Старт передачи данных через UART", config["log_filename"])
    start_time = time.time()

    try:
        while time.time() - start_time < config["duration"]:
            packet_id = int(time.time())
            params = generate_parameters()

            print("Параметры:", params)
            log_event(f"Сформирован пакет ID {packet_id}: {params}", config["log_filename"])

            save_to_csv(packet_id, params, config["csv_filename"])

            message = f"{packet_id}," + ",".join(map(str, params))
            encrypted = encrypt_message(message, config["aes_key"])
            crc = crc8(encrypted)
            full_packet = encrypted + bytes([crc])

            try:
                uart.write(full_packet)
                print("Пакет отправлен.")
                log_event(f"Отправлен пакет ID {packet_id}", config["log_filename"])
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                log_event(f"Ошибка при отправке пакета ID {packet_id}: {e}", config["log_filename"])

            time.sleep(config["interval"])

        log_event("Завершено: передача окончена", config["log_filename"])
        print("Готово.")

    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
        log_event("Передача остановлена пользователем", config["log_filename"])
    finally:
        uart.close()

if __name__ == '__main__':
    main()
