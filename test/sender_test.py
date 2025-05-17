# ========================================
# Файл: sender_test.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - Локальное тестирование генерации и шифрования LoRa-пакета
#   - Применение AES-128 + CRC8
#   - Сохранение в CSV и бинарный файл
# ========================================

import csv
import random
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ========== Настройки ==========
def get_config():
    return {
        "csv_filename": "sent_data.csv",
        "log_filename": "sender_log.txt",
        "encrypted_filename": "encrypted_packet.bin",
        "aes_key": "cat"
    }

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

# ========== Логирование ==========
def log_event(text, logfile):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Генерация параметров ==========
def generate_parameters():
    temp = random.randint(20, 30)
    pressure = random.randint(980, 1020)
    humidity = random.randint(30, 80)
    density = random.randint(1, 5)
    concentration = random.randint(50, 150)
    return [temp, pressure, humidity, density, concentration]

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
    encrypted = cipher.encrypt(pad(message.encode(), AES.block_size))
    return encrypted

# ========== Основной блок ==========
def main():
    config = get_config()
    log_event("Одноразовая передача началась", config["log_filename"])

    packet_id = int(datetime.now().timestamp())
    params = generate_parameters()
    print("Сформированы параметры:", params)
    log_event(f"Сформирован пакет ID {packet_id}: {params}", config["log_filename"])

    save_to_csv(packet_id, params, config["csv_filename"])

    message = f"{packet_id}," + ",".join(map(str, params))
    encrypted = encrypt_message(message, config["aes_key"])
    crc = crc8(encrypted)
    packet_with_crc = encrypted + bytes([crc])

    with open(config["encrypted_filename"], "wb") as f:
        f.write(packet_with_crc)

    log_event(f"Пакет ID {packet_id} зашифрован, добавлен CRC и сохранён", config["log_filename"])
    print("Содержимое сохранено в:", config["encrypted_filename"])
    print("Завершено.")

if __name__ == '__main__':
    main()
