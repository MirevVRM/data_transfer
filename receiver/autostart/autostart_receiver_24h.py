# autostart_receiver_24h.py

import csv
import os
import time
import serial
import os.path
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Configuration ==========
UART_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
AES_KEY = "cat".ljust(16)[:16].encode()
RECEIVE_DURATION = 86400  # 24 hours in seconds
START_DELAY = 1           # Delay before starting in seconds
DEBUG = False
FLUSH_INTERVAL = 60       # Flush files every 60 seconds to balance performance and data safety

# ========== Language Settings ==========
LANG = "rus"  # or "eng"

TEXTS = {
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
        'port_error': "Не удалось открыть порт {}: {}",
        'delay': "Задержка перед запуском: {} сек",
        'file_error': "Ошибка записи в файл {}: {}"
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
        'port_error': "Failed to open port {}: {}",
        'delay': "Startup delay: {} sec",
        'file_error': "Error writing to file {}: {}"
    }
}

T = TEXTS[LANG]

# ========== CRC8 ==========
def crc8(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if crc & 0x80 else crc << 1
            crc &= 0xFF
    return crc

# ========== AES Decryption ==========
def decrypt_message(ciphertext):
    try:
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode()
    except Exception:
        return None

# ========== Logging ==========
def log_event(logfile, text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {text}"
    if DEBUG:
        print(line)
    try:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()  # Force write to disk
            os.fsync(f.fileno())  # Ensure data is committed to disk
    except Exception as e:
        if DEBUG:
            print(T['file_error'].format(logfile, e))

# ========== Find Next Run Number ==========
def get_next_run_number(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    existing = [f for f in os.listdir(log_dir) if f.startswith("log_run_") and f.endswith(".txt")]
    numbers = []
    for f in existing:
        parts = f.replace("log_run_", "").replace(".txt", "")
        if parts.isdigit():
            numbers.append(int(parts))
    return max(numbers, default=0) + 1

# ========== Save to CSV ==========
def save_to_csv(csvfile, packet_id, data, crc_ok):
    header = ['packet_id', 'timestamp', 'temperature', 'pressure', 'humidity',
              'density', 'concentration', 'crc_ok']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [packet_id, timestamp] + data + [crc_ok]
    try:
        file_exists = os.path.exists(csvfile)
        with open(csvfile, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)
            f.flush()  # Force write to disk
            os.fsync(f.fileno())  # Ensure data is committed to disk
    except Exception as e:
        log_event(log_filename, T['file_error'].format(csvfile, e))

# ========== Main Loop ==========
def main():
    print(T['start'])

    run_number = get_next_run_number()
    global log_filename
    log_filename = f"logs/log_run_{run_number}.txt"
    csv_filename = f"data/received/received_run_{run_number}.csv"
    os.makedirs("data/received", exist_ok=True)

    # Startup delay
    log_event(log_filename, T['delay'].format(START_DELAY))
    time.sleep(START_DELAY)

    try:
        uart = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        log_event(log_filename, T['port_error'].format(UART_PORT, e))
        return

    log_event(log_filename, T['start_log'])
    start_time = time.time()
    last_flush = start_time

    try:
        while time.time() - start_time < RECEIVE_DURATION:
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

            # Periodically flush files to disk
            current_time = time.time()
            if current_time - last_flush >= FLUSH_INTERVAL:
                last_flush = current_time

    except KeyboardInterrupt:
        log_event(log_filename, T['user_stop'])
    finally:
        uart.close()
        log_event(log_filename, T['finished'])
        print(T['done'])

if __name__ == '__main__':
    main()
