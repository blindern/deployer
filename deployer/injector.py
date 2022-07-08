from injector import Injector, Module, provider, singleton

from deployer.config import Config
from deployer.deployer import Deployer
from deployer.lock import ServiceLocks


class AppModule(Module):
    @provider
    @singleton
    def provide_service_locks(self) -> ServiceLocks:
        return ServiceLocks()

    @provider
    @singleton
    def provide_config(self) -> Config:
        return Config()

    @provider
    @singleton
    def provide_deployer(self, config: Config) -> Deployer:
        return Deployer(config)


def build_injector() -> Injector:
    return Injector(
        [
            AppModule,
        ]
    )
