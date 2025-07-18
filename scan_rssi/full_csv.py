import asyncio
import time
import csv
import os
from bleak import BleakScanner

# ===== User Parameters =====
TARGET_NAME = "" # BLE id
MEASURE_COUNT = 50 # times of scan
MEASURE_INTERVAL = 0.1 # scan interval
grid = input("Enter the grid with space, like 2 2: ")  # Manual input for location grid
grid = grid.replace(" ", ",")

# ===== CSV File Path =====
grid_point = "" # like 16_8
recorder_id = "" # z_id
csv_path = f"./rssi_measurements_{recorder_id}_{grid_point}.csv"


async def measure_rssi():
    print(f"\n[INFO] Measuring RSSI from {TARGET_NAME} ({MEASURE_COUNT} attempts at grid {grid})...\n")
    rssi_list = []
    attempt = 0

    while len(rssi_list) < MEASURE_COUNT:
        attempt += 1
        devices = await BleakScanner.discover(timeout=1.0, return_adv=True)
        found = False

        for d, adv in devices.values():
            if adv.local_name == TARGET_NAME:
                print(f"📶 Measurement #{len(rssi_list)+1} (Attempt #{attempt}): RSSI = {adv.rssi} dBm")
                rssi_list.append(adv.rssi)
                found = True
                break

        if not found:
            print(f"⚠️  Attempt #{attempt}: {TARGET_NAME} not found → Recorded as N/A")
            rssi_list.append("N/A")

        await asyncio.sleep(MEASURE_INTERVAL)

    # ===== Compute Average and Stats =====
    valid_rssi = [r for r in rssi_list if isinstance(r, (int, float))]
    avg_rssi = sum(valid_rssi) / len(valid_rssi) if valid_rssi else "N/A"
    valid_count = len(valid_rssi)
    total_attempts = attempt

    print(f"\n✅ Completed {attempt} attempts, got {valid_count} valid RSSI readings")
    print(f"📊 Average RSSI = {avg_rssi} dBm (Grid: {grid})")

    # ===== Write to CSV =====
    fieldnames = (
        ["Grid"] +
        [f"RSSI {i+1}" for i in range(MEASURE_COUNT)] +
        ["Average RSSI", "Valid Count", "Total Attempts"]
    )
    file_exists = os.path.exists(csv_path)

    with open(csv_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(fieldnames)
        writer.writerow([grid] + rssi_list + [avg_rssi, valid_count, total_attempts])

    print(f"\n💾 Data written to: {csv_path}")

if __name__ == "__main__":
    asyncio.run(measure_rssi())
