📡 data_transfer

<p align="center">
  <img src="docs/img/General scheme.png" alt="LoRa telemetry system diagram" width="800">
</p>

Python-based LoRa telemetry system for Raspberry Pi 4 and E22-900T22S (UART).  
Features AES-128 encryption, CRC8 checksum, CSV logging, and automated data collection.

> RSSI and SNR are not available due to UART module limitations.

---

📁 Project Structure

```
data_transfer/
├── sender/          → main LoRa transmitter (UART)
├── receiver/        → main LoRa receiver (UART)
├── test/            → local tests (no LoRa hardware needed)
├── logs_csv/        → tools for data download and cleanup
```

---

📦 Required Python Libraries

The following Python libraries must be installed manually:

pyserial  
pycryptodome

These are used for UART communication and AES encryption, respectively.


---

🔧 Main Components

- `sender.py`: encrypts and sends telemetry packets over UART
- `receiver.py`: receives packets, validates CRC8, decrypts, and logs
- `sender_test.py`: local test of AES + CRC8 encryption
- `receiver_test.py`: decrypts and checks test packet from file
- `download_data.py`: copies result files from Raspberry Pi via SCP
- `clear_data.py`: removes logs and data files for a clean session
- `main_controller.py`: runs a simple CLI for testing and clearing

---

📦 Data Output

- `sent_data.csv` / `received_data.csv`: telemetry and status
- `sender_log.txt` / `receiver_log.txt`: detailed event logs
- `encrypted_packet.bin`: raw binary packet with AES + CRC8

---

🔐 Encryption & Integrity

- AES-128 in ECB mode for confidentiality
- CRC8 checksum added for packet integrity
- Default key: `"cat"` (can be changed in config)

---

👥 Authors

- Snopkov D. I.  
- Shimpf A. A.  
📅 Version: May 2025

