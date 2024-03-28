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
            force_deploy=False,
        )

        assert mock_push_changes.call_count == 2

    @patch("deployer.repo.TempRepo.push_changes")
    def test_ansible(
        self,
        mock_push_changes: MagicMock,
        injector: Injector,
    ):
        mock_push_changes.side_effect = [None]

        config = injector.get(Config)
        deployer = Deployer(config=config)

        deployer.handle(
            service=config.services["test-service1"],
            attributes={
                "value": "hello",
            },
            force_deploy=False,
        )

        mock_push_changes.assert_called_once()

    @patch("deployer.repo.TempRepo.push_changes")
    @patch("deployer.deployer.Deployer._ansible_deploy")
    def test_skip_no_change(
        self,
        mock_ansible_deploy: MagicMock,
        mock_push_changes: MagicMock,
        injector: Injector,
    ):
        # Avoid any real side effect.
        mock_ansible_deploy.return_value = None
        mock_push_changes.return_value = None

        config = injector.get(Config)
        deployer = Deployer(config=config)

        deployer.handle(
            service=config.services["test-service1"],
            attributes={},
            force_deploy=False,
        )

        mock_ansible_deploy.assert_not_called()

    @patch("deployer.repo.TempRepo.push_changes")
    @patch("deployer.deployer.Deployer._ansible_deploy")
    def test_force_deploy_for_no_changes(
        self,
        mock_ansible_deploy: MagicMock,
        mock_push_changes: MagicMock,
        injector: Injector,
    ):
        # Avoid any real side effect.
        mock_ansible_deploy.return_value = None
        mock_push_changes.return_value = None

        config = injector.get(Config)
        deployer = Deployer(config=config)

        deployer.handle(
            service=config.services["test-service1"],
            attributes={},
            force_deploy=True,
        )

        mock_ansible_deploy.assert_called_once()
        mock_push_changes.assert_not_called()
