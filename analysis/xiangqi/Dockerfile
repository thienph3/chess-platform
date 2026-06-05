FROM python:3.11-slim

# Build Pikafish from source (hoặc download binary)
RUN apt-get update && apt-get install -y curl build-essential git && \
    git clone --depth 1 https://github.com/official-pikafish/Pikafish.git /tmp/pikafish && \
    cd /tmp/pikafish/src && make -j$(nproc) build ARCH=x86-64 && \
    cp /tmp/pikafish/src/pikafish /usr/local/bin/pikafish && \
    rm -rf /tmp/pikafish && apt-get purge -y build-essential git && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shared/ /app/shared/
COPY xiangqi/pyproject.toml .
RUN pip install --no-cache-dir .

COPY xiangqi/ .

EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
