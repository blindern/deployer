import os

os.environ["VALID_TOKENS"] = "abc"
os.environ["GIT_REPO"] = "git@github.com:blindern/deployer-test.git"
os.environ["GIT_CRYPT_KEY_PATH"] = "git-crypt-key-test"
os.environ["SERVICES_FILE"] = "tests/services.json"
