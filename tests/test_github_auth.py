import json
from unittest.mock import MagicMock, mock_open, patch

import pytest

from deployer.github_auth import GitHubAuth


class TestInjectTokenIntoUrl:
    def test_basic(self):
        url = "https://github.com/blindern/drift.git"
        result = GitHubAuth.inject_token_into_url(url, "ghp_abc123")
        assert result == "https://x-access-token:ghp_abc123@github.com/blindern/drift.git"

    def test_preserves_path(self):
        url = "https://github.com/org/repo.git"
        result = GitHubAuth.inject_token_into_url(url, "tok")
        assert result == "https://x-access-token:tok@github.com/org/repo.git"


class TestRedactToken:
    def test_replaces_token(self):
        text = "Cloning into https://x-access-token:secret123@github.com/o/r.git"
        result = GitHubAuth.redact_token(text, "secret123")
        assert "secret123" not in result
        assert "[REDACTED]" in result

    def test_no_match(self):
        text = "Nothing to redact here"
        result = GitHubAuth.redact_token(text, "secret123")
        assert result == text


class TestGetToken:
    @patch("deployer.github_auth.urllib.request.urlopen")
    @patch("builtins.open", mock_open(read_data="fake-private-key"))
    def test_creates_installation_token(self, mock_urlopen: MagicMock):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"token": "ghs_test_token"}
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with patch("deployer.github_auth.jwt.encode", return_value="fake-jwt"):
            auth = GitHubAuth(
                app_id="12345",
                private_key_path="/fake/key.pem",
                installation_id="67890",
            )
            token = auth.get_token()

        assert token == "ghs_test_token"
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        assert "/installations/67890/access_tokens" in req.full_url

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_missing_key_file_raises(self, _mock_open: MagicMock):
        with pytest.raises(FileNotFoundError):
            GitHubAuth(
                app_id="12345",
                private_key_path="/nonexistent/key.pem",
                installation_id="67890",
            )
