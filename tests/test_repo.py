import subprocess
from pathlib import Path

import pytest

from deployer.config import Config
from deployer.repo import RaceException, TempRepo


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.fixture
def repo(config: Config):
    repo = TempRepo(config)
    yield repo
    repo.cleanup()


class TestRepo:
    def test_push__trigger_race(self, config: Config, repo: TempRepo):
        config.skip_git_push = False

        repo.checkout()

        def cmd(*args: str):
            subprocess.run(args, cwd=repo.path).check_returncode()

        # change history so we are no longer fast-forward
        cmd("git", "fetch", "--depth", "2")
        cmd("git", "reset", "--hard", "HEAD~1")

        Path(Path(repo.path) / "dummy").write_text("")

        cmd("git", "add", "dummy")
        cmd("git", "commit", "-m", "Race test")

        with pytest.raises(RaceException):
            repo.push_changes()
