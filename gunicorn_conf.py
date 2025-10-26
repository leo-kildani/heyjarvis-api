# gunicorn_conf.py
import multiprocessing

# For t3.small/t2.micro memory, start conservative; tune up if stable.
workers = max(2, multiprocessing.cpu_count() * 2 + 1)  # usually 3 on 1 vCPU
bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
graceful_timeout = 30
keepalive = 5

# Access/error logs to stdout/stderr (Docker-friendly)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Slightly smaller worker connections; your endpoints are CPU-light but may hit VLM I/O
worker_connections = 1000
