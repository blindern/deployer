FROM python:3.13-slim@sha256:8d4ea9d6915221b2d78e39e0dea0c714a4affb73ba74e839dbf6f76c524f78e4

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      git \
      git-crypt \
      openssh-client \
    ; \
    rm -rf /var/lib/apt/lists/*; \
    git config --global user.name "Deployer"; \
    git config --global user.email "it-gruppa@foreningenbs.no"

COPY --from=ghcr.io/astral-sh/uv:0.9.0 /uv /uvx /bin/

WORKDIR /code
COPY uv.lock pyproject.toml /code/

RUN uv sync --locked --no-dev

COPY deployer /code/deployer
COPY container/ssh_config /root/.ssh/config

EXPOSE 8000
CMD ["uv", "run", "--no-dev", "gunicorn", "--timeout", "900", "-b", "0.0.0.0:8000", "--threads", "4", "deployer.app:app"]
