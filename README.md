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
├── sender/                  → main LoRa transmitter (UART)
│   ├── sender.py            → manual version
│   ├── clear_data.py
│   └── autostart/           
│       └── autostart_sender.py → non-interactive version for auto-run
├── receiver/                
│   ├── receiver.py          → manual version
│   ├── clear_data.py
│   └── autostart/           
│       └── autostart_receiver.py → non-interactive version for auto-run
├── logs_csv/                → data tools
│   ├── clear_data.py
│   └── download_data.py
├── test/                    → local tests (no LoRa hardware)
│   ├── sender_test.py
│   ├── receiver_test.py
│   ├── main_controller.py
│   └── clear_data.py
```

---

📦 Required Python Libraries

Install manually:

* `pyserial` → UART communication
* `pycryptodome` → AES encryption (ECB) and padding

Use `pip install pyserial pycryptodome` if needed.

---

🔧 Main Components

* `autostart_sender.py`: auto-run version of the sender with no user interaction
* `autostart_receiver.py`: auto-run version of the receiver
* `sender.py`: legacy interactive version for UART transmission
* `receiver.py`: legacy interactive version for receiving + logging
* `sender_test.py`: test AES/CRC without hardware
* `receiver_test.py`: validate decryption and CRC
* `download_data.py`: pulls logs via SCP
* `clear_data.py`: removes `.csv` and `.txt` files for fresh sessions
* `main_controller.py`: basic test/control runner (legacy)

---

⚙️ Auto-Run Behavior

Both `autostart_sender.py` and `autostart_receiver.py`:

* Run without `input()`
* Use preset configs (see top of each file)
* Log to file (`*_log.txt`)
* Designed for Raspberry Pi autostart via `systemd`, `rc.local`, or `crontab`

Example timing:

* Sender runs for 150s with 15s interval and 5s start delay
* Receiver listens for 170s without delay

---

📦 Data Output

* `sent_data.csv` / `received_data.csv`: telemetry records
* `sender_log.txt` / `receiver_log.txt`: events + debug logs
* `encrypted_packet.bin`: optional raw binary (for test/debug)

---

🔐 Encryption & Integrity

* AES-128 in ECB mode (default key: `"cat"`)
* CRC8 checksum to detect corrupted packets
* Configurable in `CONFIG` dict at the top of each script

---

## 👥 Authors

* Snopkov D. I.
* Shimpf A. A.
  📅 Version: May 2025
