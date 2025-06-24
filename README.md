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
experimental_results_logs_csv/         # Main folder for data and logs
├── data/
│   ├── sender/                        → CSV data sent in each run
│   └── received/                      → CSV data received and verified
├── logs/
│   ├── sender_log/                    → transmission logs (TXT)
│   └── receiver_log/                  → reception logs (TXT)
├── combined_data.xlsx                 → final merged Excel dataset

logs_csv/                              # Scripts for working with CSV data
├── clear_data.py                      → utility to clean all logs and CSVs
├── download_data.py                   → fetch CSV/logs from external source (e.g. SBC)

receiver/
├── receiver.py                        → manual receiver: AES + CRC + save to CSV
├── clear_data.py                      → clear local receiver logs/data
└── autostart/
    ├── autostart_receiver.py         → legacy automated receiver script (short duration)
    └── autostart_receiver_24h.py     → automated 24-hour headless receiver script

sender/
├── sender.py                          → manual sender: AES + CRC packet transmitter
├── clear_data.py                      → clear local sender logs/data
└── autostart/
    ├── autostart_sender.py           → legacy automated sender script (short duration)
    └── autostart_sender_24h.py       → automated 24-hour headless sender script

test/                                  # Unit test and control files
├── sender_test.py                     → offline test: AES packet encryption
├── receiver_test.py                   → offline test: AES + CRC decryption
├── main_controller.py                 → legacy or integration test script
└── clear_data.py                      → test data cleaner

Instructions/                          # User guides
├── Instruction_rus.txt                → инструкция (на русском)
└── Instruction_eng.txt                → user manual (in English)

docs/img/                              → diagrams, figures, illustrations
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
| `autostart_sender.py`   | Legacy auto-start sender: short duration, auto-shutdown |
| `autostart_sender_24h.py` | Auto-start sender: generates packets every 30s for 24h |
| `autostart_receiver.py` | Legacy auto-start receiver: short duration, auto-shutdown |
| `autostart_receiver_24h.py` | Auto-start receiver: listens and logs for 24 hours |
| `sender_test.py`        | Tests encryption/CRC generation (no UART needed)       |
| `receiver_test.py`      | Tests decryption/CRC checking (offline)                |
| `download_data.py`      | Downloads `.csv`/`.txt` from device via SCP            |
| `clear_data.py`         | Clears `.csv` and `.txt` files for a fresh run         |
| `main_controller.py`    | Legacy control script                                  |

---

## ⚙️ Auto-Run Behavior

| Script                   | Duration | Interval | Delay | Shutdown | Description                       |
|--------------------------|----------|----------|-------|----------|-----------------------------------|
| `autostart_sender.py`    | 150s     | 15s      | 5s    | ✅ Yes    | Legacy sender with short duration |
| `autostart_sender_24h.py`| 24h      | 30s      | 5s    | ❌ No     | 24-hour sender, no auto-shutdown  |
| `autostart_receiver.py`  | 170s     | —        | 1s    | ✅ Yes    | Legacy receiver with short duration |
| `autostart_receiver_24h.py` | 24h   | —        | 1s    | ❌ No     | 24-hour receiver, no auto-shutdown |

* All scripts require **no user interaction** and use internal `CONFIG` parameters.
* Automatically **generate unique filenames** per run:
  * `data/sender/sent_run_<n>.csv`
  * `data/received/received_run_<n>.csv`
  * `logs/log_run_<n>.txt`
* Designed for **autostart on Raspberry Pi**:
  * `systemd` unit
  * `crontab @reboot`
  * or `/etc/rc.local`

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
