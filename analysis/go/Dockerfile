FROM python:3.11-slim

# Download KataGo binary + model
RUN apt-get update && apt-get install -y curl unzip && \
    curl -L -o /tmp/katago.zip https://github.com/lightvector/KataGo/releases/download/v1.15.3/katago-v1.15.3-eigen-linux-x64.zip && \
    unzip /tmp/katago.zip -d /tmp/katago && \
    cp /tmp/katago/katago /usr/local/bin/katago && chmod +x /usr/local/bin/katago && \
    mkdir -p /usr/local/share/katago && \
    curl -L -o /usr/local/share/katago/model.bin.gz https://media.katagotraining.org/uploaded/networks/models/kata1/kata1-b18c384nbt-s9131461376-d4087399203.bin.gz && \
    cp /tmp/katago/default_gtp.cfg /usr/local/share/katago/config.cfg && \
    rm -rf /tmp/katago /tmp/katago.zip && apt-get purge -y unzip && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shared/ /app/shared/
COPY go/pyproject.toml .
RUN pip install --no-cache-dir .

COPY go/ .

EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
