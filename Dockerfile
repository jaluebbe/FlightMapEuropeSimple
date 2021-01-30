FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip install aiofiles redis
COPY static /app/static
COPY static/flightmap_europe_simple.html /app/static/index.html
COPY static/statistics_redis.html /app/static/statistics.html
COPY backend_vrs_db.py /app/
COPY backend_fastapi.py /app/main.py
