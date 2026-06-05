FROM python:3.11-slim

# Download Rapfi binary from GitHub releases (7z archive)
RUN apt-get update && apt-get install -y curl p7zip-full && \
    curl -L -o /tmp/rapfi.7z https://github.com/dhbloo/rapfi/releases/download/250615/Rapfi-engine.7z && \
    7z x /tmp/rapfi.7z -o/tmp/rapfi && \
    find /tmp/rapfi -name "pbrain-rapfi*" -type f | head -1 | xargs -I{} cp {} /usr/local/bin/rapfi && \
    chmod +x /usr/local/bin/rapfi && \
    rm -rf /tmp/rapfi /tmp/rapfi.7z && apt-get purge -y p7zip-full && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shared/ /app/shared/
COPY gomoku/pyproject.toml .
RUN pip install --no-cache-dir .

COPY gomoku/ .

EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
