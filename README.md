## 📡 data_transfer

<p align="center">
  <img src="docs/img/General scheme.png" alt="LoRa telemetry system diagram" width="800">
</p>

Python-based LoRa telemetry system for Raspberry Pi 4 and E22-900T22S (UART).  
Features AES-128 encryption, CRC8 checksum, CSV logging, and automated data collection.

> RSSI and SNR are not available due to UART module limitations.

---

## 📁 Project Structure

```
data_transfer/
├── sender/
│   ├── sender.py                  → manual interactive transmitter
│   ├── clear_data.py              → delete sent logs/data
│   └── autostart/
│       └── autostart_sender.py    → auto-run sender with AES + CRC + shutdown
├── receiver/
│   ├── receiver.py                → manual interactive receiver
│   ├── clear_data.py              → delete received logs/data
│   └── autostart/
│       └── autostart_receiver.py  → auto-run receiver with AES + CRC + shutdown
├── logs_csv/
│   ├── clear_data.py              → remove all CSV and log files
│   └── download_data.py           → pull logs and data via SCP
├── test/
│   ├── sender_test.py             → offline packet encryption test
│   ├── receiver_test.py           → offline packet decryption + CRC test
│   ├── main_controller.py         → legacy control/test stub
│   └── clear_data.py              → cleanup for tests
├── Instructions/
│   ├── Instruction_rus.txt        → user manual (RU)
│   └── Instruction_eng.txt        → user manual (EN)
├── docs/img/                      → illustrations and diagrams
```

---

## 📦 Required Python Libraries

Install via pip:

```bash
pip install pyserial pycryptodome
```

* `pyserial`: UART communication
* `pycryptodome`: AES encryption + PKCS7 padding

---

## 🔧 Main Components

| Script                  | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `sender.py`             | Manual sender: prompts for run number + distance       |
| `receiver.py`           | Manual receiver: logs and stores packets interactively |
| `autostart_sender.py`   | Auto-start sender: uses internal config, shuts down    |
| `autostart_receiver.py` | Auto-start receiver: listens, logs, then shuts down    |
| `sender_test.py`        | Tests encryption/CRC generation (no UART needed)       |
| `receiver_test.py`      | Tests decryption/CRC checking (offline)                |
| `download_data.py`      | Downloads `.csv`/`.txt` from device via SCP            |
| `clear_data.py`         | Clears `.csv` and `.txt` files for a fresh run         |
| `main_controller.py`    | Legacy control script                                  |

---

## ⚙️ Auto-Run Behavior

Both `autostart_sender.py` and `autostart_receiver.py`:

* Require **no user interaction**
* Use internal `CONFIG` parameters
* Automatically **generate unique filenames** per run:

  * `data/sent_run_<n>.csv`
  * `data/received_run_<n>.csv`
  * `logs/log_run_<n>.txt`
* Designed for **autostart on Raspberry Pi**:

  * `systemd` unit
  * `crontab @reboot`
  * or `/etc/rc.local`

🕒 **Default timing (example):**

| Role     | Duration | Interval | Delay | Shutdown |
| -------- | -------- | -------- | ----- | -------- |
| Sender   | 150 s    | 15 s     | 5 s   | ✅ Yes    |
| Receiver | 170 s    | —        | 1 s   | ✅ Yes    |

---

## 📦 Data Output

| Mode      | CSV Filename Format            | Log Filename Format           |
| --------- | ------------------------------ | ----------------------------- |
| Manual    | `sent_run_<n>_<distance>m.csv` | `log_run_<n>_<distance>m.txt` |
| Autostart | `sent_run_<n>.csv`             | `log_run_<n>.txt`             |

> All logs and telemetry files are saved automatically under `/data` and `/logs`.

---

## 🔐 Encryption & Integrity

* **AES-128**, ECB mode, 16-byte key (`"cat"`, padded)
* **PKCS7** padding
* **CRC8** checksum to verify data integrity
* Logic unified between sender and receiver

---

## 👥 Authors

* **Snopkov D. I.**
* **Shimpf A. A.**

📅 **Version:** June 2025
