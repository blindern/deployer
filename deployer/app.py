from deployer.app_factory import configure_logging, create_app
from deployer.injector import build_injector

configure_logging()

app = create_app(build_injector())
