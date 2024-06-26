import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from deployer.config import Config
from deployer.repo import RaceException, TempRepo
from deployer.services import ServiceModel

logger = logging.getLogger(__name__)


class Deployer:
    def __init__(self, config: Config):
        self.config = config

    def _patch_content(
        self, previous_content: dict[str, str], patch_values: dict[str, str]
    ) -> Any:
        cpy = previous_content.copy()
        for key, value in patch_values.items():
            cpy[key] = value

            prev = previous_content.get(key, None)
            if prev != value:
                logger.info(f"Update {key} from '{prev}' to '{value}'")

        return cpy

    def _write_changes(
        self,
        repo: TempRepo,
        service: ServiceModel,
        deployer_json_file: Path,
        patch_values: dict[str, str],
    ) -> None:
        attempt = 0
        while attempt < 4:
            attempt += 1
            try:
                repo.commit_changes(f"Update {service.service_name}")
                repo.push_changes()
                return
            except RaceException:
                logger.info("Detected race while pushing")

                repo.fetch_latest_and_reset()

                previous_content: dict[str, str] = json.loads(
                    deployer_json_file.read_text()
                )
                updated_content = self._patch_content(previous_content, patch_values)
                if previous_content == updated_content:
                    logger.info("No changes found after deploy")
                    return

                self._write_deployer_file(deployer_json_file, updated_content)

        raise RuntimeError("Too many attempts to write changes")

    def _ansible_deploy(self, cwd: Path, tag: str, host: str):
        cmd = ["ansible-playbook", "site.yml", "-i", "hosts", "-l", host, "-t", tag]
        logger.info(f"Will run: {cmd}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )

        assert process.stdout is not None
        while process.stdout.readable():
            line = process.stdout.readline()
            if not line:
                break
            logger.info(f"[ANSIBLE] {line.decode()}".strip())

        returncode = process.wait()

        if returncode != 0:
            raise RuntimeError(f"Ansible failed with exit code {returncode}")

    def _write_deployer_file(
        self, deployer_json_file: Path, content: dict[str, str]
    ) -> None:
        deployer_json_file.write_text(json.dumps(content, indent="  ") + "\n")

    def handle(
        self, service: ServiceModel, attributes: dict[str, str], force_deploy: bool
    ):
        patch_values: dict[str, str] = {}
        for key, value in attributes.items():
            if key not in service.mappings:
                raise ValueError(f"'{key}' not found in mappings")
            patch_values[service.mappings[key]] = value

        repo = TempRepo(self.config)
        try:
            logger.info("Checking out repo")
            repo.checkout()

            deployer_json_file: Path = (
                Path(repo.path)
                / self.config.ansible_path
                / self.config.deployer_json_file
            )
            if not deployer_json_file.exists():
                raise RuntimeError(f"File '{deployer_json_file}' not found")

            previous_content: dict[str, str] = json.loads(
                deployer_json_file.read_text()
            )
            updated_content = self._patch_content(previous_content, patch_values)
            if previous_content == updated_content:
                logger.info("No changes found")
                if not force_deploy:
                    return
            else:
                self._write_deployer_file(deployer_json_file, updated_content)

            start = time.time()

            self._ansible_deploy(
                cwd=Path(repo.path) / self.config.ansible_path,
                tag=service.ansible_tag,
                host=service.ansible_host,
            )

            logger.info(f"Ansible deploy completed in {time.time() - start} s")

            if previous_content != updated_content:
                self._write_changes(
                    repo=repo,
                    service=service,
                    deployer_json_file=deployer_json_file,
                    patch_values=patch_values,
                )

        finally:
            repo.cleanup()
