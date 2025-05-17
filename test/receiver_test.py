# ========================================
# Файл: receiver_test.py
# Авторы: Snopkov D. I., Shimpf A. A.
# Версия: май 2025
# Назначение:
#   - Локальное тестирование приёма и расшифровки LoRa-пакета
#   - Проверка CRC8 и расшифровка AES-128
#   - Сохранение результата в CSV и лог-файл
# ========================================

import csv
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Настройки ==========
def get_config():
    return {
        "csv_filename": "received_data.csv",
        "log_filename": "receiver_log.txt",
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

# ========== Расшифровка AES ==========
def decrypt_message(ciphertext, key_str):
    key = key_str.ljust(16)[:16].encode()
    cipher = AES.new(key, AES.MODE_ECB)
    try:
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode()
    except Exception:
        return None

# ========== Сохранение в CSV ==========
def save_to_csv(packet_id, data, crc_ok, filename):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity',
              'density', 'concentration', 'crc_ok']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data + [crc_ok]
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

# ========== Основной блок ==========
def main():
    config = get_config()
    log_event("Начало одноразового приёма", config["log_filename"])

    try:
        with open(config["encrypted_filename"], "rb") as f:
            packet = f.read()

        if len(packet) < 17:
            log_event("Пакет слишком короткий", config["log_filename"])
            print("Ошибка: слишком короткий пакет.")
            return

        encrypted = packet[:-1]
        received_crc = packet[-1]
        calculated_crc = crc8(encrypted)
        crc_ok = (received_crc == calculated_crc)

        if not crc_ok:
            log_event(f"Ошибка CRC: получено {received_crc}, ожидалось {calculated_crc}", config["log_filename"])
            print("Ошибка CRC! Пакет отброшен.")
            return

        decrypted = decrypt_message(encrypted, config["aes_key"])
        if decrypted is None:
            log_event("Ошибка расшифровки пакета", config["log_filename"])
            print("Ошибка расшифровки.")
            return

        print("Расшифрованные данные:", decrypted)
        log_event(f"Расшифрован пакет: {decrypted}", config["log_filename"])

        parts = decrypted.split(",")
        if len(parts) != 6:
            log_event("Неверный формат данных", config["log_filename"])
            return

        packet_id = int(parts[0])
        data = list(map(int, parts[1:]))

        save_to_csv(packet_id, data, crc_ok, config["csv_filename"])
        log_event(f"Пакет ID {packet_id} сохранён", config["log_filename"])
        print("Завершено.")

    except FileNotFoundError:
        log_event("Файл зашифрованных данных не найден", config["log_filename"])
        print("Файл `encrypted_packet.bin` не найден.")

    except Exception as e:
        log_event(f"Ошибка выполнения: {e}", config["log_filename"])
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()
