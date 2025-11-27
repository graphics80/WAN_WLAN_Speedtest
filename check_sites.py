#!/usr/bin/env python3
"""
Prüft jede Minute, ob bestimmte Websites erreichbar sind und loggt:
- timestamp
- url
- reachable (0/1)
- http_status
- response_time_ms
- error (falls vorhanden)
"""

import requests
import datetime
import csv
import os
from typing import List
from common_influx import write_influx

SITES: List[str] = [
    "https://20min.ch",
    "https://www.google.ch",
    "https://www.bzz.ch",
    "https://www.blick.ch",
    "https://wiki.bzz.ch",
    "https://moodle.bzz.ch",
]

LOGFILE = os.path.expanduser("~/http_check_log.csv")
TIMEOUT_SECONDS = 5


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


def check_site(url: str):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    reachable = 0
    status_code = None
    response_time_ms = None
    error = ""

    try:
        resp = requests.get(url, timeout=TIMEOUT_SECONDS)
        status_code = resp.status_code
        response_time_ms = resp.elapsed.total_seconds() * 1000.0
        if 200 <= resp.status_code < 400:
            reachable = 1
    except Exception as e:
        error = str(e)

    row = [ts, url, reachable, status_code, response_time_ms, error]
    append_row(LOGFILE, row)

    #Influx:
    fields = {
        "reachable": reachable,
        "http_status": status_code if status_code is not None else -1,
        "response_time_ms": response_time_ms if response_time_ms is not None else -1.0,
    }
    tags = {"url": url}
    # timestamp haben wir schon als ts-String, hier neu erzeugen:
    write_influx("http_check", tags, fields)

    print(f"[{ts}] {url}: reachable={reachable}, status={status_code}, rt={response_time_ms} ms")


def main():
    header = ["timestamp", "url", "reachable", "http_status", "response_time_ms", "error"]
    ensure_csv_with_header(LOGFILE, header)

    for url in SITES:
        check_site(url)


if __name__ == "__main__":
    main()
