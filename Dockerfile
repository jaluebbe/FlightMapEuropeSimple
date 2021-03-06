FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
RUN pip install aiofiles redis
COPY static /app/static
COPY backend_vrs_db.py /app/
COPY backend_fastapi.py /app/main.py
