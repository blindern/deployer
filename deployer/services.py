import json
from pathlib import Path

from pydantic import BaseModel, StrictStr


class ServiceModel(BaseModel):
    service_name: StrictStr
    ansible_tag: StrictStr
    ansible_host: StrictStr
    # Entries that belong to this service.
    # api-value => deployer.json key
    mappings: dict[StrictStr, StrictStr]


class ServicesModel(BaseModel):
    __root__: dict[StrictStr, ServiceModel]


def load_services_file(path: str) -> dict[str, ServiceModel]:
    data = json.loads(Path(path).read_text())
    model = ServicesModel.parse_obj(data)
    return model.__root__
