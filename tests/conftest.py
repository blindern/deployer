import os
from deployer.services import SERVICES, Service

os.environ["VALID_TOKENS"] = "abc"
os.environ["GIT_REPO"] = "git@github.com:blindern/deployer-test.git"
os.environ["GIT_CRYPT_KEY_PATH"] = "git-crypt-key-test"

SERVICES["test-service1"] = Service(
    service_name="service1",
    ansible_tag="service1",
    ansible_host="host1",
    mappings={
        "value": "deployer_service_1_value",
    },
)

SERVICES["test-service2"] = Service(
    service_name="service2",
    ansible_tag="service2",
    ansible_host="host2",
    mappings={
        "value": "deployer_service_2_value",
    },
)
