FROM python:3.13-slim@sha256:452ed869040b0d92371f1d444da1997de6cd468b74c23149c0062c1c8b9ffbb3

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

COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /bin/

WORKDIR /code
COPY uv.lock pyproject.toml /code/

RUN uv sync --locked --no-dev

COPY deployer /code/deployer
COPY container/ssh_config /root/.ssh/config

EXPOSE 8000
CMD ["uv", "run", "--no-dev", "gunicorn", "--timeout", "900", "-b", "0.0.0.0:8000", "--threads", "4", "deployer.app:app"]
