FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip install aiofiles
COPY static /app/static
COPY backend_vrs_db.py /app/
COPY backend_fastapi.py /app/main.py
