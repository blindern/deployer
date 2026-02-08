import os

os.environ["VALID_TOKENS"] = "abc"
os.environ["GIT_REPO"] = "https://github.com/blindern/deployer-test.git"
os.environ["GIT_CRYPT_KEY_PATH"] = "git-crypt-key-test"
os.environ["SERVICES_FILE"] = "tests/services.json"

# fbs-deployer-test app defaults (PEM file path can be overridden)
os.environ.setdefault("GITHUB_APP_ID", "2824239")
os.environ.setdefault("GITHUB_APP_INSTALLATION_ID", "108886929")
os.environ.setdefault("GITHUB_APP_PRIVATE_KEY_PATH", "test-app-key.pem")
