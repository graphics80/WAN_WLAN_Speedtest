# Repository Guidelines

## Project Structure & Module Organization
- Core collectors live in the repo root: `check_sites.py` (HTTP reachability), `wan_speedtest.py` (speed tests), and shared utilities in `common_influx.py`.
- Dependencies are in `requirements.txt`. A local virtualenv (`.venv/`) is expected but not committed.
- CSV logs are written to user paths (`~/http_check_log.csv`, `~/wan_speedtest_log.csv`). Ensure the runtime user can write there when scheduling.
- InfluxDB writes use the shared helper; keep new measurements aligned with existing tags/fields to preserve dashboard compatibility.

## Build, Test, and Development Commands
- Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- HTTP check: `python check_sites.py`; WAN speed: `python wan_speedtest.py` (both write CSV + Influx).
- Influx defaults: `INFLUX_URL` and `INFLUX_DB` env vars override `common_influx.py` fallbacks (`http://localhost:8086/write`, `netmon`).

## Coding Style & Naming Conventions
- Follow PEP 8; 4-space indentation; snake_case for functions/variables; ALL_CAPS for constants.
- Put shared logic in `common_influx.py`; mirror the pattern: ISO timestamps with `timespec="seconds"`, append to CSV, then push fields/tags to Influx with defaults for missing data (-1 or empty string).

## Testing Guidelines
- No tests yet; add `pytest` under `tests/` (e.g., `tests/test_check_sites.py`).
- Mock network calls (`requests`) and Influx writes; assert CSV rows and field/tag construction.
- Run with `pytest` from the repo root; keep tests fast.

## Commit & Pull Request Guidelines
- Use concise, imperative commit subjects (e.g., "Add latency logging for site checks"). Group related changes into single commits.
- PRs should describe intent, list key changes, and note operational impacts (scheduling, new endpoints, log paths). Link to any issue/ticket and include screenshots or sample log/Influx lines when relevant.

## Docker-Based Testing
- Build: `docker compose build`; start stack: `docker compose up -d influxdb grafana check-sites wan-speedtest`.
- One-off runs: `docker compose run --rm collector` (both scripts), or `docker compose run --rm collector python check_sites.py`.
- Scheduled containers: `check-sites` (every minute) and `wan-speedtest` (every 30 minutes); CSVs land in `./logs/`.
- Grafana: auto-starts on port 3000 (admin/admin). Datasource and dashboard (`WAN / WLAN`) are auto-provisioned from `grafana/provisioning/`. Data source UID `ef5d72wmn4kjkf`, dashboard UID `ef5dcooiib6kga`.
- Shell: `docker run --rm -it -v "$PWD":/app -w /app python:3.11-slim bash` then `pip install -r requirements.txt`.
- Configure Influx via env (`INFLUX_URL`, `INFLUX_DB`); compose defaults to `http://influxdb:8086/write`.

## Operations & Configuration Tips
- Before scheduling via cron/systemd or compose services, confirm the venv path and writable home (or mount `./logs/` when containerized).
- Keep credentials and host overrides out of VCS; prefer env vars or a local config file excluded by `.gitignore` when extending Influx settings.
