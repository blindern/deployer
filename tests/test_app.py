import time
from threading import Thread
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from injector import Injector

from deployer.app_factory import create_app
from deployer.config import Config
from deployer.injector import build_injector


@pytest.fixture
def injector() -> Injector:
    return build_injector()


@pytest.fixture
def app(injector: Injector) -> Flask:
    config: Config = injector.get(Config)
    config.valid_tokens = ["abc"]
    return create_app(injector)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


class TestApp:
    def test_invalid_json(self, client: FlaskClient):
        response = client.post(
            "/deploy",
            json={"abc": "def"},
            headers={
                "authorization": "bearer abc",
            },
        )
        assert response.status_code == 400

    def test_invalid_auth(self, client: FlaskClient):
        response = client.post(
            "/deploy",
            json={"abc": "def"},
            headers={
                "authorization": "bearer invalid",
            },
        )
        assert response.status_code == 401

    def test_missing_auth(self, client: FlaskClient):
        response = client.post(
            "/deploy",
            json={"abc": "def"},
        )
        assert response.status_code == 401

    @patch("deployer.repo.TempRepo.push_changes")
    @patch("deployer.deployer.Deployer._ansible_deploy")
    def test_success(
        self,
        mock_ansible_deploy: MagicMock,
        mock_push_changes: MagicMock,
        client: FlaskClient,
    ):
        # Avoid any real side effect.
        mock_ansible_deploy.return_value = None
        mock_push_changes.return_value = None

        response = client.post(
            "/deploy",
            json={
                "service": "test-service1",
                "attributes": {"value": "hello"},
            },
            headers={
                "authorization": "bearer abc",
            },
        )
        assert response.status_code == 200, response.text

    @patch("deployer.repo.TempRepo.push_changes")
    @patch("deployer.deployer.Deployer._ansible_deploy")
    @patch("deployer.deployer.Deployer.handle")
    def test_lock(
        self,
        mock_handle: MagicMock,
        mock_ansible_deploy: MagicMock,
        mock_push_changes: MagicMock,
        client: FlaskClient,
    ):
        # Avoid any real side effect.
        mock_ansible_deploy.return_value = None
        mock_push_changes.return_value = None

        def side_effect(*args, **kwargs):
            time.sleep(1)

        mock_handle.side_effect = side_effect

        def req():
            response = client.post(
                "/deploy",
                json={
                    "service": "test-service1",
                    "attributes": {"value": "hello"},
                },
                headers={
                    "authorization": "bearer abc",
                },
            )
            assert response.status_code == 200, response.text

        tr1 = Thread(target=req)
        tr2 = Thread(target=req)

        start = time.time()

        tr1.start()
        tr2.start()

        tr1.join()
        tr2.join()

        end = time.time()
        duration = end - start
        assert duration > 2
