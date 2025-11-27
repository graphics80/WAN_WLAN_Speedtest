#!/usr/bin/env python3
import datetime
import os
import requests
from typing import Dict, Any, Optional

INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086/write")
INFLUX_DB = os.environ.get("INFLUX_DB", "netmon")


def escape_tag_value(value: str) -> str:
    """
    Escaping für Tag-Werte nach Influx Line Protocol:
    Spaces, Kommas und Gleichzeichen werden mit Backslash escaped.
    """
    s = str(value)
    s = s.replace(" ", "\\ ")
    s = s.replace(",", "\\,")
    s = s.replace("=", "\\=")
    return s


def escape_field_string(value: str) -> str:
    """
    Escaping für String-Fields:
    Backslashes und doppelte Anführungszeichen escapen.
    """
    s = str(value)
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    return s


def write_influx(
    measurement: str,
    tags: Dict[str, str],
    fields: Dict[str, Any],
    timestamp: Optional[datetime.datetime] = None,
) -> None:
    """
    Schreibt einen einzelnen Datensatz im Influx Line Protocol nach InfluxDB.
    """
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()

    # Tags bauen
    tag_list = []
    for k, v in tags.items():
        tag_list.append(f"{k}={escape_tag_value(v)}")
    tag_str = ",".join(tag_list)

    # Fields bauen
    field_parts = []
    for k, v in fields.items():
        if v is None:
            continue
        if isinstance(v, (int, float)):
            field_parts.append(f"{k}={v}")
        else:
            field_parts.append(f'{k}="{escape_field_string(v)}"')
    field_str = ",".join(field_parts)

    # Zeitstempel in ns
    ns = int(timestamp.timestamp() * 1_000_000_000)

    # Line-Protocol-Zeile
    if tag_str:
        line = f"{measurement},{tag_str} {field_str} {ns}"
    else:
        line = f"{measurement} {field_str} {ns}"

    params = {"db": INFLUX_DB}
    r = requests.post(INFLUX_URL, params=params, data=line)
    r.raise_for_status()
