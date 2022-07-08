import logging
import os

from dotenv import load_dotenv

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
            "GIT_REPO", "git@github.com:blindern/deployer-test.git"
        )

        if self.skip_git_push:
            logger.warning("Will not push to Git on changes")

    @staticmethod
    def _require_env(name: str) -> str:
        if name not in os.environ:
            raise RuntimeError(f"Missing env {name}")
        return os.environ[name]
