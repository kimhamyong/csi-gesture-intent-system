import os
import pcap
import dpkt
import keyboard
import pandas as pd
import numpy as np
import time
import requests
import json
import cfg
from math import log10
from datetime import datetime

output_path = '../data'
os.makedirs(output_path, exist_ok=True)

BANDWIDTH = cfg.EXTRACTOR_CONFIG['bandwidth']
SAMPLE_RATE = 2
NSUB = int(BANDWIDTH * 3.2)
SERVER_URL = '' #서버 URL

def truncate(num, n):
    return float(int(num * (10**n)) / (10**n))

def capture_csi(nicname, duration):
    sniffer = pcap.pcap(name=nicname, promisc=True, immediate=True, timeout_ms=50)
    sniffer.setfilter('udp and port 5500')
    column = ['mac', 'time'] + ['_' + str(i) for i in range(0, NSUB)]
    mac_dict = {}
    before_ts = 0.0
    start_time = time.time()

    for ts, pkt in sniffer:
        if time.time() - start_time > duration or keyboard.is_pressed('s'):
            break
        if int(ts) == int(before_ts):
            cur_ts = truncate(ts, SAMPLE_RATE)
            bef_ts = truncate(before_ts, SAMPLE_RATE)
            if cur_ts == bef_ts:
                before_ts = ts
                continue

        eth = dpkt.ethernet.Ethernet(pkt)
        ip = eth.data
        udp = ip.data

        mac = udp.data[4:10].hex()
        if mac not in mac_dict:
            mac_dict[mac] = pd.DataFrame(columns=column)

        csi = udp.data[18:]
        csi_np = np.frombuffer(csi, dtype=np.int16, count=NSUB * 2)
        csi_np = csi_np.reshape((1, NSUB * 2))
        csi_cmplx = np.fft.fftshift(csi_np[:, ::2] + 1.j * csi_np[:, 1::2], axes=(1,))
        csi_df = pd.DataFrame(csi_cmplx)
        csi_df.insert(0, 'mac', mac)
        csi_df.insert(1, 'time', ts)
        columns = {i: '_' + str(i) for i in range(0, NSUB)}
        csi_df.rename(columns=columns, inplace=True)

        mac_dict[mac] = pd.concat([mac_dict[mac], csi_df], ignore_index=True)
        before_ts = ts

    return mac_dict

def save_csv_and_json(df, csv_path, save_json):
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")

    if save_json:
        csi_only = df.drop(columns=['mac', 'time'])
        sequence = csi_only.applymap(lambda x: str(x)).values.tolist()
        json_path = csv_path.replace(".csv", ".json")
        with open(json_path, 'w') as f:
            json.dump({"sequence": sequence}, f, indent=2)
        print(f"Saved JSON: {json_path}")

def send_to_server(df):
    csi_only = df.drop(columns=['mac', 'time'])
    sequence = csi_only.applymap(lambda x: str(x)).values.tolist()
    payload = {"sequence": sequence}

    try:
        response = requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            print("Upload successful")
        else:
            print(f"Upload failed (status {response.status_code})")
        print("Server response:", response.text)
    except Exception as e:
        print("Upload error:", e)


    try:
        response = requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            print("Upload successful")
        else:
            print(f"Upload failed (status {response.status_code})")
    except Exception as e:
        print("Upload error:", e)

def main():
    print("---- CSI Capture Tool ----")
    print("Choose mode:\n1 - Save only\n2 - Send to server")
    print("--------------------------")
    mode = input("Choose mode (1 or 2): ").strip()

    if mode == '1':
        print("\n---- [Save Only Mode] ----")
        filename_base = input("Set file name base (e.g. 'test'): ").strip()

        repeat_input = input("Set repeat number ('-' for infinite, '-1' to restart): ").strip()
        if repeat_input == '-1':
            return main()
        elif repeat_input == '-':
            repeat_count = -1
        else:
            try:
                repeat_count = int(repeat_input)
                if repeat_count < 0:
                    print("Repeat count must not be negative.")
                    return main()
            except ValueError:
                print("Invalid input. Restarting...")
                return main()

        try:
            duration = int(input("Set capture duration (seconds): "))
            delay = int(input("Set delay before capture (seconds): "))
        except ValueError:
            print("Invalid input. Restarting...")
            return main()

        save_json = input("Save also as JSON? (y/n): ").strip().lower() == 'y'

        count = 1
        while repeat_count == -1 or count <= repeat_count:
            if keyboard.is_pressed('s'):
                print("Capture stopped by user input.")
                break
            print(f"\n---- Capture #{count} ----")
            print(f"Waiting {delay} seconds...")
            time.sleep(delay)
            print("Capturing...")

            mac_dict = capture_csi('wlan0', duration)
            if keyboard.is_pressed('s'):
                print("Capture stopped by user input.")
                break
            for mac in mac_dict:
                filename = f"{filename_base}_{count}.csv"
                csv_path = os.path.join(output_path, filename)
                save_csv_and_json(mac_dict[mac], csv_path, save_json)
            count += 1

    elif mode == '2':
        print("\n---- [Server Upload Mode] ----")
        repeat_input = input("Set repeat number ('-' for infinite, '-1' to restart): ").strip()
        if repeat_input == '-1':
            return main()
        elif repeat_input == '-':
            repeat_count = -1
        else:
            try:
                repeat_count = int(repeat_input)
                if repeat_count < 0:
                    print("Repeat count must not be negative.")
                    return main()
            except ValueError:
                print("Invalid input. Restarting...")
                return main()

        try:
            duration = int(input("Set capture duration (seconds): "))
            delay = int(input("Set delay before capture (seconds): "))
        except ValueError:
            print("Invalid input. Restarting...")
            return main()

        count = 1
        while repeat_count == -1 or count <= repeat_count:
            if keyboard.is_pressed('s'):
                print("Capture stopped by user input.")
                break
            print(f"\n---- Capture #{count} ----")
            print(f"Waiting {delay} seconds...")
            time.sleep(delay)
            print("Capturing...")

            mac_dict = capture_csi('wlan0', duration)
            if keyboard.is_pressed('s'):
                print("Capture stopped by user input.")
                break
            for mac in mac_dict:
                filename = f"capture_{count}.csv"
                csv_path = os.path.join(output_path, filename)
                mac_dict[mac].to_csv(csv_path, index=False)
                print(f"Saved CSV: {csv_path}")
                send_to_server(mac_dict[mac])
            count += 1

    else:
        print("Invalid mode. Restarting...\n")
        return main()

if __name__ == '__main__':
    main()
