FROM python:3.13-slim@sha256:a0779d7c12fc20be6ec6b4ddc901a4fd7657b8a6bc9def9d3fde89ed5efe0a3d

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

COPY --from=ghcr.io/astral-sh/uv:0.9.10 /uv /uvx /bin/

WORKDIR /code
COPY uv.lock pyproject.toml /code/

RUN uv sync --locked --no-dev

COPY deployer /code/deployer
COPY container/ssh_config /root/.ssh/config

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)"]
CMD ["uv", "run", "--no-dev", "gunicorn", "--timeout", "900", "-b", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "deployer.app:app"]
