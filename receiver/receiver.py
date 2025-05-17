# ========================================
# Файл: receiver.py (UART-версия)
# Автор: Snopkov D. I., Shimpf A.A.
# Версия: май 2025
# Назначение:
#   - Приём зашифрованных пакетов с CRC8 по UART от E22-900T22S
#   - Расшифровка AES и сохранение в CSV
# ========================================

import csv
import time
import serial
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Логирование ==========
def log_event(text, logfile):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== Настройки ==========
def get_config():
    print("Ввод параметров скрипта (Enter — по умолчанию)")
    try:
        delay = int(input("Задержка перед запуском (сек): ") or 0)
        duration = int(input("Время приёма (сек): ") or 120)
    except ValueError:
        print("Ошибка ввода. Применяются значения по умолчанию.")
        delay = 0
        duration = 120

    return {
        "delay": delay,
        "duration": duration,
        "csv_filename": "received_data.csv",
        "log_filename": "receiver_log.txt",
        "aes_key": "cat",
        "uart_port": "/dev/ttyUSB0",
        "baudrate": 9600
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
def save_to_csv(packet_id, data, crc_ok, rssi, snr, filename):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity',
              'density', 'concentration', 'crc_ok', 'rssi', 'snr']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data + [crc_ok, rssi, snr]
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

    log_event("Приём по UART запущен", config["log_filename"])
    start_time = time.time()

    try:
        while time.time() - start_time < config["duration"]:
            raw = uart.read(33)  # 32 байта AES + 1 байт CRC
            if not raw or len(raw) < 17:
                continue

            data, received_crc = raw[:-1], raw[-1]
            calculated_crc = crc8(data)
            crc_ok = (received_crc == calculated_crc)

            if not crc_ok:
                log_event("CRC не совпадает — пакет отброшен", config["log_filename"])
                continue

            decrypted = decrypt_message(data, config["aes_key"])
            if decrypted is None:
                log_event("Ошибка расшифровки пакета", config["log_filename"])
                continue

            parts = decrypted.split(",")
            if len(parts) != 6:
                log_event("Неверный формат расшифрованных данных", config["log_filename"])
                continue

            try:
                packet_id = int(parts[0])
                payload = list(map(int, parts[1:]))
            except ValueError:
                log_event("Ошибка преобразования данных", config["log_filename"])
                continue

            rssi = None  # по умолчанию — если модуль не вставляет RSSI
            snr = None

            save_to_csv(packet_id, payload, crc_ok, rssi, snr, config["csv_filename"])
            log_event(f"Пакет ID {packet_id} сохранён", config["log_filename"])

    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
        log_event("Приём остановлен вручную", config["log_filename"])
    finally:
        uart.close()
        log_event("Приём завершён", config["log_filename"])
        print("Готово.")

if __name__ == '__main__':
    main()
