FROM python:3.11-slim

RUN apt-get update && apt-get install -y stockfish curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Opening book (committed in repo)
COPY chess/book.bin /app/book.bin

# Copy shared module
COPY shared/ /app/shared/

# Copy chess service
COPY chess/pyproject.toml .
RUN pip install --no-cache-dir .

COPY chess/ .

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
