# ========================================
# Файл: receiver.py (UART-версия)
# Автор: Snopkov D. I., Shimpf A.A.
# Версия: май 2025
# Назначение:
#   - RU: Приём зашифрованных пакетов с CRC8 по UART от E22-900T22S
#   - EN: Receiving AES-encrypted CRC8 packets via UART from E22-900T22S
#   - Расшифровка AES и сохранение в CSV
# ========================================

import csv
import time
import serial
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== Выбор языка ==========
def choose_language():
    lang = input("Выберите язык / Choose language [Rus/Eng] (по умолчанию: Rus): ").strip().lower()
    return 'eng' if lang == 'eng' else 'rus'

LANG = choose_language()

TEXT = {
    'rus': {
        'start': "=== UART-Приёмник (receiver.py) ===",
        'input_prompt': "Ввод параметров скрипта (Enter — по умолчанию)",
        'delay': "Задержка перед запуском (сек): ",
        'duration': "Время приёма (сек): ",
        'input_error': "Ошибка ввода. Применяются значения по умолчанию.",
        'wait': "Ожидание {} сек перед запуском...",
        'port_error': "Не удалось открыть порт {}: {}",
        'start_log': "Приём по UART запущен",
        'crc_fail': "CRC не совпадает — пакет отброшен",
        'decrypt_fail': "Ошибка расшифровки пакета",
        'format_error': "Неверный формат расшифрованных данных",
        'value_error': "Ошибка преобразования данных",
        'packet_saved': "Пакет ID {} сохранён",
        'interrupted': "Прервано пользователем.",
        'user_stop': "Приём остановлен вручную",
        'finished': "Приём завершён",
        'done': "Готово."
    },
    'eng': {
        'start': "=== UART Receiver (receiver.py) ===",
        'input_prompt': "Enter script parameters (press Enter for default)",
        'delay': "Delay before start (sec): ",
        'duration': "Reception time (sec): ",
        'input_error': "Input error. Default values will be used.",
        'wait': "Waiting {} seconds before start...",
        'port_error': "Failed to open port {}: {}",
        'start_log': "UART reception started",
        'crc_fail': "CRC mismatch — packet dropped",
        'decrypt_fail': "Packet decryption failed",
        'format_error': "Invalid decrypted data format",
        'value_error': "Data conversion error",
        'packet_saved': "Packet ID {} saved",
        'interrupted': "Interrupted by user.",
        'user_stop': "Reception stopped by user",
        'finished': "Reception completed",
        'done': "Done."
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

# ========== Настройки ==========
def get_config():
    print(T['input_prompt'])
    try:
        delay = int(input(T['delay']) or 0)
        duration = int(input(T['duration']) or 120)
    except ValueError:
        print(T['input_error'])
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
            raw = uart.read(33)  # 32 байта AES + 1 байт CRC
            if not raw or len(raw) < 17:
                continue

            data, received_crc = raw[:-1], raw[-1]
            calculated_crc = crc8(data)
            crc_ok = (received_crc == calculated_crc)

            if not crc_ok:
                log_event(T['crc_fail'], config["log_filename"])
                continue

            decrypted = decrypt_message(data, config["aes_key"])
            if decrypted is None:
                log_event(T['decrypt_fail'], config["log_filename"])
                continue

            parts = decrypted.split(",")
            if len(parts) != 6:
                log_event(T['format_error'], config["log_filename"])
                continue

            try:
                packet_id = int(parts[0])
                payload = list(map(int, parts[1:]))
            except ValueError:
                log_event(T['value_error'], config["log_filename"])
                continue

            rssi = None
            snr = None

            save_to_csv(packet_id, payload, crc_ok, rssi, snr, config["csv_filename"])
            log_event(T['packet_saved'].format(packet_id), config["log_filename"])

    except KeyboardInterrupt:
        print("\n" + T['interrupted'])
        log_event(T['user_stop'], config["log_filename"])
    finally:
        uart.close()
        log_event(T['finished'], config["log_filename"])
        print(T['done'])

if __name__ == '__main__':
    main()
