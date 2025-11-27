FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY check_sites.py wan_speedtest.py common_influx.py ./

# Default command runs the HTTP checks; override in docker-compose or docker run as needed.
CMD ["python", "check_sites.py"]
