#!/usr/bin/env python3
"""
WAN-Speedtest via speedtest-cli

Misst alle 30 Minuten:
- Ping (ms)
- Download (Mbit/s)
- Upload (Mbit/s)
- genutzter Speedtest-Server

Log: ~/wan_speedtest_log.csv
"""

import datetime
import csv
import os
from common_influx import write_influx


LOGFILE = os.path.expanduser("~/wan_speedtest_log.csv")


def ensure_csv_with_header(path: str, header: list) -> None:
    if not os.path.isfile(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def append_row(path: str, row: list) -> None:
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def run_speedtest():
    try:
        import speedtest
    except ImportError:
        raise SystemExit("speedtest-cli (Python-Modul) nicht installiert. Bitte: pip3 install speedtest-cli")

    st = speedtest.Speedtest()
    st.get_best_server()
    st.download()
    st.upload()

    results = st.results.dict()

    ping_ms = results.get("ping")
    download_mbit = results.get("download", 0) / 1_000_000.0  # bits/s -> Mbit/s
    upload_mbit = results.get("upload", 0) / 1_000_000.0
    server = results.get("server", {}).get("host", "")

    return ping_ms, download_mbit, upload_mbit, server


def main():
    header = ["timestamp", "ping_ms", "download_mbit", "upload_mbit", "server"]
    ensure_csv_with_header(LOGFILE, header)

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    print(f"[{ts}] Starte Speedtest...")

    try:
        ping_ms, dl, ul, server = run_speedtest()
    except Exception as e:
        # bei Fehler trotzdem loggen
        row = [ts, None, None, None, f"ERROR: {e}"]
        append_row(LOGFILE, row)
        print(f"Fehler beim Speedtest: {e}")
        return

    row = [ts, ping_ms, dl, ul, server]
    append_row(LOGFILE, row)

    fields = {
        "ping_ms": ping_ms if ping_ms is not None else -1.0,
        "download_mbit": dl if dl is not None else -1.0,
        "upload_mbit": ul if ul is not None else -1.0,
    }
    tags = {"server": server}
    write_influx("wan_speedtest", tags, fields)

    print(f"[{ts}] Speedtest: ping={ping_ms:.1f} ms, down={dl:.2f} Mbit/s, up={ul:.2f} Mbit/s, server={server}")


if __name__ == "__main__":
    main()
