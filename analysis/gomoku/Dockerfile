FROM python:3.11-slim

# Download Rapfi binary from GitHub releases
RUN apt-get update && apt-get install -y curl unzip && \
    curl -L -o /tmp/rapfi.zip https://github.com/dhbloo/rapfi/releases/latest/download/rapfi-linux-x64.zip && \
    unzip /tmp/rapfi.zip -d /tmp/rapfi && \
    cp /tmp/rapfi/pbrain-rapfi /usr/local/bin/rapfi && chmod +x /usr/local/bin/rapfi && \
    rm -rf /tmp/rapfi /tmp/rapfi.zip && apt-get purge -y unzip && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shared/ /app/shared/
COPY gomoku/pyproject.toml .
RUN pip install --no-cache-dir .

COPY gomoku/ .

EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
