import logging
import subprocess
from tempfile import TemporaryDirectory

from deployer.config import Config

logger = logging.getLogger(__name__)


class RaceException(RuntimeError):
    pass


class TempRepo:
    def __init__(self, config: Config):
        self._repo_dir = TemporaryDirectory(prefix="deployer_")
        self.path = self._repo_dir.name
        self.config = config

    def _exec(self, cmd: list[str]) -> subprocess.CompletedProcess:
        res = subprocess.run(cmd, cwd=self._repo_dir.name, capture_output=True)
        if res.stdout is not None:
            logger.info(f"STDOUT: {res.stdout!r}")
        if res.stderr is not None:
            logger.info(f"STDERR: {res.stderr!r}")

        return res

    def checkout(self):
        self._exec(
            ["git", "clone", "--depth", "1", self.config.git_repo, "."]
        ).check_returncode()
        self._exec(["git-crypt", "unlock", self.config.git_crypt_key_path])
        logger.info("Repo decrypted")

    def fetch_latest_and_reset(self):
        self._exec(["git", "fetch", "origin"]).check_returncode()
        self._exec(["git", "reset", "--hard", "origin/main"]).check_returncode()

    def commit_changes(self, message: str):
        self._exec(["git", "commit", "-am", message]).check_returncode()

    def push_changes(self):
        """
        Raises RaceException if it cannot be pushed.
        """
        if self.config.skip_git_push:
            logger.info("Skipping git push")
            return

        res = self._exec(["git", "push"])
        if res.stderr is not None and "non-fast-forward" in str(res.stderr):
            raise RaceException()
        res.check_returncode()

    def cleanup(self):
        self._repo_dir.cleanup()
