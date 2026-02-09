import json
import logging
import time
import urllib.request
from urllib.parse import urlparse, urlunparse

import jwt

logger = logging.getLogger(__name__)


class GitHubAuth:
    def __init__(self, app_id: str, private_key_path: str, installation_id: str):
        self._app_id = app_id
        self._installation_id = installation_id
        with open(private_key_path) as f:
            self._private_key = f.read()
        self.slug = self._fetch_app_slug()

    def _fetch_app_slug(self) -> str:
        token_jwt = self._create_jwt()
        req = urllib.request.Request(
            "https://api.github.com/app",
            headers={
                "Authorization": f"Bearer {token_jwt}",
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["slug"]

    def get_token(self) -> str:
        token_jwt = self._create_jwt()
        return self._create_installation_token(token_jwt)

    def _create_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 600,
            "iss": self._app_id,
        }
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    def _create_installation_token(self, token_jwt: str) -> str:
        url = (
            f"https://api.github.com/app/installations"
            f"/{self._installation_id}/access_tokens"
        )
        req = urllib.request.Request(
            url,
            method="POST",
            headers={
                "Authorization": f"Bearer {token_jwt}",
                "Accept": "application/vnd.github+json",
            },
            data=b"{}",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["token"]

    @staticmethod
    def inject_token_into_url(url: str, token: str) -> str:
        parsed = urlparse(url)
        host = parsed.hostname
        if parsed.port:
            host = f"{parsed.hostname}:{parsed.port}"
        authed = parsed._replace(netloc=f"x-access-token:{token}@{host}")
        return urlunparse(authed)

    @staticmethod
    def redact_token(text: str, token: str) -> str:
        return text.replace(token, "[REDACTED]")
