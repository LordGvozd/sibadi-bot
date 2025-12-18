FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"
ENV PYTHONUNBUFFERED=1

ADD pyproject.toml .

RUN uv sync --no-group dev 

ENV PYTHONPATH="/app/"

COPY src/ ./src
CMD ["uv", "run", "--no-dev", "src/main.py"]
