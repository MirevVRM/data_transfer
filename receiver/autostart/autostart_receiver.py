# ========================================
# Файл: receiver.py (UART-версия) — автозапуск
# Версия: май 2025
# ========================================

import csv
import time
import serial
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Константы и конфиг ==========
DEBUG = False

CONFIG = {
    "LANG": "rus",
    "DELAY_BEFORE_START": 0,
    "RECEIVE_DURATION": 120,
    "UART_PORT": "/dev/ttyUSB0",
    "BAUDRATE": 9600,
    "AES_KEY": "cat",
    "CSV_FILENAME": "received_data.csv",
    "LOG_FILENAME": "receiver_log.txt",
}

TEXT = {
    'rus': {
        'start': "=== UART-Приёмник (receiver.py) ===",
        'wait': "Ожидание {} сек перед запуском...",
        'port_error': "Не удалось открыть порт {}: {}",
        'start_log': "Приём по UART запущен",
        'crc_fail': "CRC не совпадает — пакет отброшен",
        'decrypt_fail': "Ошибка расшифровки пакета",
        'format_error': "Неверный формат расшифрованных данных",
        'value_error': "Ошибка преобразования данных",
        'packet_saved': "Пакет ID {} сохранён",
        'user_stop': "Приём остановлен вручную",
        'finished': "Приём завершён",
        'done': "Готово."
    },
    'eng': {
        'start': "=== UART Receiver (receiver.py) ===",
        'wait': "Waiting {} seconds before start...",
        'port_error': "Failed to open port {}: {}",
        'start_log': "UART reception started",
        'crc_fail': "CRC mismatch — packet dropped",
        'decrypt_fail': "Packet decryption failed",
        'format_error': "Invalid decrypted data format",
        'value_error': "Data conversion error",
        'packet_saved': "Packet ID {} saved",
        'user_stop': "Reception stopped by user",
        'finished': "Reception completed",
        'done': "Done."
    }
}

T = TEXT[CONFIG["LANG"]]

# ========== Логирование ==========
def log_event(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    if DEBUG:
        print(line)
    with open(CONFIG["LOG_FILENAME"], "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== CRC8 ==========
def crc8(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if crc & 0x80 else crc << 1
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
def save_to_csv(packet_id, data, crc_ok, rssi, snr):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity',
              'density', 'concentration', 'crc_ok', 'rssi', 'snr']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data + [crc_ok, rssi, snr]
    file_exists = False
    try:
        with open(CONFIG["CSV_FILENAME"], 'r'):
            file_exists = True
    except FileNotFoundError:
        pass
    with open(CONFIG["CSV_FILENAME"], 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

# ========== Основной цикл ==========
def main():
    if DEBUG:
        print(T['start'])

    if CONFIG["DELAY_BEFORE_START"] > 0:
        log_event(T['wait'].format(CONFIG["DELAY_BEFORE_START"]))
        time.sleep(CONFIG["DELAY_BEFORE_START"])

    try:
        uart = serial.Serial(
            port=CONFIG["UART_PORT"],
            baudrate=CONFIG["BAUDRATE"],
            timeout=1
        )
    except Exception as e:
        log_event(T['port_error'].format(CONFIG["UART_PORT"], e))
        return

    log_event(T['start_log'])
    start_time = time.time()

    try:
        while time.time() - start_time < CONFIG["RECEIVE_DURATION"]:
            raw = uart.read(33)
            if not raw or len(raw) < 17:
                continue

            data, received_crc = raw[:-1], raw[-1]
            calculated_crc = crc8(data)
            crc_ok = (received_crc == calculated_crc)

            if not crc_ok:
                log_event(T['crc_fail'])
                continue

            decrypted = decrypt_message(data, CONFIG["AES_KEY"])
            if decrypted is None:
                log_event(T['decrypt_fail'])
                continue

            parts = decrypted.split(",")
            if len(parts) != 6:
                log_event(T['format_error'])
                continue

            try:
                packet_id = int(parts[0])
                payload = list(map(int, parts[1:]))
            except ValueError:
                log_event(T['value_error'])
                continue

            rssi = None
            snr = None

            save_to_csv(packet_id, payload, crc_ok, rssi, snr)
            log_event(T['packet_saved'].format(packet_id))

    except KeyboardInterrupt:
        log_event(T['user_stop'])
    finally:
        uart.close()
        log_event(T['finished'])
        if DEBUG:
            print(T['done'])

if __name__ == '__main__':
    main()
