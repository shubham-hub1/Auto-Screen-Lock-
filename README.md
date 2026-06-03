# Bluetooth Auto Lock for Windows

Automatically lock your Windows PC when a trusted Bluetooth device (such as your phone, smartwatch, or earbuds) goes out of range.

## Features

* Locks Windows automatically when the selected Bluetooth device is no longer detected.
* Supports monitoring by Bluetooth MAC address or device name.
* Configurable scan interval and timeout period.
* Lightweight and easy to run in the background.
* Uses the native Windows lock mechanism.

## Requirements

* Windows 10/11
* Python 3.9+
* Bluetooth adapter enabled

### Install Dependencies

```bash
pip install bleak pywin32
```

## Usage

### Monitor by MAC Address

```bash
python bluetooth_lock.py --mac AA:BB:CC:DD:EE:FF
```

### Monitor by Device Name

```bash
python bluetooth_lock.py --name "MyPhone"
```

### Custom Scan Interval and Timeout

```bash
python bluetooth_lock.py --name "MyPhone" --interval 5 --timeout 20
```

## Command-Line Options

| Option       | Description                                            |
| ------------ | ------------------------------------------------------ |
| `--mac`      | Bluetooth MAC address to monitor                       |
| `--name`     | Bluetooth device name to monitor                       |
| `--interval` | Seconds between Bluetooth scans                        |
| `--timeout`  | Time in seconds before locking after device disappears |

## How It Works

1. The application continuously scans for nearby Bluetooth devices.
2. If the specified device is detected, the timer is reset.
3. When the device remains undetected for the configured timeout period, Windows is automatically locked.
4. Monitoring continues after the lock event.

## Example

```bash
python bluetooth_lock.py --name "ShubhamPhone" --interval 5 --timeout 15
```

If `ShubhamPhone` is not detected for 15 seconds, the workstation will lock automatically.

## Security Notes

* Bluetooth discovery is not always perfectly reliable.
* Use a reasonable timeout value (10–30 seconds) to avoid accidental locks.
* The tool should be considered a convenience feature and not a replacement for standard security practices.

