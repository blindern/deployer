FROM python:3.12-slim

# renovate: datasource=pypi depName=ansible
ENV ANSIBLE_VERSION=9.6.1

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
    git config --global user.email "it-gruppa@foreningenbs.no"; \
    # Installing Ansible takes a lot of space.
    # Keep it in this layer to prevent it to be invalidated
    # for other dependency changes.
    pip install ansible==$ANSIBLE_VERSION

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN set -eux; \
    poetry config virtualenvs.create false; \
    poetry install --no-interaction --no-ansi

COPY deployer /code/deployer
COPY container/ssh_config /root/.ssh/config

EXPOSE 8000
CMD ["gunicorn", "--timeout", "900", "-b", "0.0.0.0:8000", "--threads", "4", "deployer.app:app"]
