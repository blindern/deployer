FROM python:3.14-slim@sha256:5cfac249393fa6c7ebacaf0027a1e127026745e603908b226baa784c52b9d99b

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

COPY --from=ghcr.io/astral-sh/uv:0.9.4 /uv /uvx /bin/

WORKDIR /code
COPY uv.lock pyproject.toml /code/

RUN uv sync --locked --no-dev

COPY deployer /code/deployer
COPY container/ssh_config /root/.ssh/config

EXPOSE 8000
CMD ["uv", "run", "--no-dev", "gunicorn", "--timeout", "900", "-b", "0.0.0.0:8000", "--threads", "4", "deployer.app:app"]
