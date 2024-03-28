import json
from pathlib import Path

from pydantic import BaseModel, RootModel, StrictStr


class ServiceModel(BaseModel):
    service_name: StrictStr
    ansible_tag: StrictStr
    ansible_host: StrictStr
    # Entries that belong to this service.
    # api-value => deployer.json key
    mappings: dict[StrictStr, StrictStr]


ServicesModel = RootModel[dict[StrictStr, ServiceModel]]


def load_services_file(path: str) -> dict[str, ServiceModel]:
    data = json.loads(Path(path).read_text())
    model = ServicesModel.model_validate(data)
    return model.root
