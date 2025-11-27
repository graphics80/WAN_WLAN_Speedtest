# WAN Monitor

Lightweight collectors that log HTTP reachability and WAN speed tests to CSV and InfluxDB, with an auto-provisioned Grafana dashboard.

## Quick Start (Docker)
- Build and start everything: `docker compose build` then `docker compose up -d influxdb grafana check-sites wan-speedtest`
- Grafana: http://localhost:3000 (admin/admin). Datasource (uid `ef5d72wmn4kjkf`, DB `netmon`) and dashboard “WAN / WLAN” are preloaded.
- Logs: CSVs persist to `./logs/` via volume mounts.

## Services
- `check-sites`: runs every minute, writes `~/http_check_log.csv` (in container mapped to `./logs/http_check_log.csv`) and Influx measurement `http_check`.
- `wan-speedtest`: runs every 30 minutes, writes `~/wan_speedtest_log.csv` and Influx measurement `wan_speedtest`.
- `influxdb`: InfluxDB 1.8 with database `netmon`.
- `grafana`: Preprovisioned dashboard at http://localhost:3000.

## Native (non-Docker)
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`
3) Set Influx env vars if not local: `export INFLUX_URL=http://<host>:8086/write INFLUX_DB=netmon`
4) Run collectors manually: `python check_sites.py` and `python wan_speedtest.py`

## Configuration
- Influx defaults live in `common_influx.py` but are overridden by env vars `INFLUX_URL` and `INFLUX_DB`.
- Adjust schedules in `docker-compose.yml` by editing the `sleep` intervals in the `check-sites` and `wan-speedtest` commands.
- Provisioning files: `grafana/provisioning/datasources/` and `grafana/provisioning/dashboards/`.

## Checking Data
- CSV tails: `tail -n 5 logs/http_check_log.csv` and `tail -n 5 logs/wan_speedtest_log.csv`
- Influx queries (from host): `docker compose exec influxdb influx -execute "USE netmon; SHOW MEASUREMENTS"` then select as needed.
- Grafana panels use queries:
  - `SELECT mean("response_time_ms") FROM "http_check" WHERE $timeFilter GROUP BY time($__interval), "url"`
  - `SELECT distinct("download_mbit") FROM "autogen"."wan_speedtest" WHERE $timeFilter GROUP BY time($__interval)`

## Troubleshooting
- Docker not reachable: ensure Docker Desktop/daemon is running.
- No data in Grafana: confirm `check-sites` and `wan-speedtest` containers are up (`docker compose ps`) and that InfluxDB is reachable at `influxdb:8086` inside the network.
