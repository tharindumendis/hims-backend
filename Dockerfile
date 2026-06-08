FROM python:3.11-slim-bookworm

WORKDIR /app

# 1. Update system packages to patch vulnerabilities
# 2. Install libaio1t64 (required for Oracle)
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libaio1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]