from unittest.mock import MagicMock, patch

import pytest
from injector import Injector

from deployer.config import Config
from deployer.deployer import Deployer
from deployer.injector import build_injector
from deployer.repo import RaceException


@pytest.fixture
def injector() -> Injector:
    return build_injector()


class TestDeployer:
    @patch("deployer.repo.TempRepo.push_changes")
    @patch("deployer.deployer.Deployer._ansible_deploy")
    def test_write_retry(
        self,
        mock_ansible_deploy: MagicMock,
        mock_push_changes: MagicMock,
        injector: Injector,
    ):
        # Avoid any real side effect.
        mock_ansible_deploy.return_value = None
        mock_push_changes.side_effect = [RaceException, None]

        config = injector.get(Config)
        deployer = Deployer(config=config)

        deployer.handle(
            service=config.services["test-service1"],
            attributes={
                "value": "hello",
            },
        )

        assert mock_push_changes.call_count == 2

    @patch("deployer.repo.TempRepo.push_changes")
    def test_ansible(
        self,
        mock_push_changes: MagicMock,
        injector: Injector,
    ):
        mock_push_changes.side_effect = [RaceException, None]

        config = injector.get(Config)
        deployer = Deployer(config=config)

        deployer.handle(
            service=config.services["test-service1"],
            attributes={
                "value": "hello",
            },
        )

        assert mock_push_changes.assert_called_once
