FROM python:3.12-slim

WORKDIR /app

# Only install the bare essentials for psutil/pandas
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create empty files so the Python scripts don't crash on start
RUN touch sat_system.log medic_status.json

COPY . .

EXPOSE 7860

# Force unbuffered output so you see logs immediately in HF
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
