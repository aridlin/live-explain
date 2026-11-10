FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl1 libgl1 libglib2.0-0 libxkbcommon0 libdbus-1-3 libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV QT_QPA_PLATFORM=offscreen HOME=/tmp XDG_CACHE_HOME=/tmp/cache \
    LIVE_EXPLAIN_STATE_DIR=/state LIVE_EXPLAIN_ORIGIN=https://prol.aridlin.pl
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "live_explain.web", "--host", "0.0.0.0", "--port", "8080"]
