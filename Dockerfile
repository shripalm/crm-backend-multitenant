FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps for asyncpg build if needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# RUN ./scripts/run-em.sh
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
