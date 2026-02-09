import logging
import os

from dotenv import load_dotenv

from deployer.github_auth import GitHubAuth
from deployer.services import load_services_file

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.ansible_path = "ansible"
        self.deployer_json_file = "group_vars/all/deployer.json"
        self.valid_tokens = self._require_env("VALID_TOKENS").split(",")
        self.git_crypt_key_path = self._require_env("GIT_CRYPT_KEY_PATH")
        self.skip_git_push = os.environ.get("SKIP_GIT_PUSH", "false") == "true"
        self.git_repo = os.environ.get(
            "GIT_REPO", "https://github.com/blindern/deployer-test.git"
        )

        app_id = self._require_env("GITHUB_APP_ID")
        self.github_auth = GitHubAuth(
            app_id=app_id,
            private_key_path=self._require_env("GITHUB_APP_PRIVATE_KEY_PATH"),
            installation_id=self._require_env("GITHUB_APP_INSTALLATION_ID"),
        )

        slug = self.github_auth.slug
        self.git_committer_name = f"{slug}[bot]"
        self.git_committer_email = f"{app_id}+{slug}[bot]@users.noreply.github.com"

        if self.skip_git_push:
            logger.warning("Will not push to Git on changes")

        self.services_file = self._require_env("SERVICES_FILE")
        self.services = load_services_file(self.services_file)

    @staticmethod
    def _require_env(name: str) -> str:
        if name not in os.environ:
            raise RuntimeError(f"Missing env {name}")
        return os.environ[name]
