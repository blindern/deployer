FROM python:3.10-slim

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      git \
      git-crypt \
      openssh-client \
    ; \
    rm -rf /var/lib/apt/lists/*; \
    pip install poetry; \
    git config --global user.name "Deployer"; \
    git config --global user.email "it-gruppa@foreningenbs.no"

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN set -eux; \
    poetry config virtualenvs.create false; \
    poetry install --no-interaction --no-ansi

COPY deployer /code/deployer
COPY container/ssh_config /root/.ssh/config

EXPOSE 8000
CMD ["gunicorn", "--timeout", "900", "-b", "0.0.0.0:8000", "deployer.app:app"]
