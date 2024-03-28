import os

from flask import Blueprint, Response, current_app, request
from pydantic import BaseModel, StrictBool, StrictStr, ValidationError
from werkzeug.exceptions import BadRequest

from deployer.config import Config
from deployer.deployer import Deployer
from deployer.lock import ServiceLocks


class DeployRequest(BaseModel):
    service: StrictStr
    attributes: dict[StrictStr, StrictStr] = {}
    # Normally deploys only when an attribute is changed.
    # Set this to true to always do a deploy for the service.
    # If no attributes are given this will default to true.
    forceDeploy: StrictBool = False


def text_response(value, status):
    return Response(value, mimetype="text/plain", status=status)


api = Blueprint("api", __name__)


@api.route("/deploy", methods=["POST"])
def deploy(service_locks: ServiceLocks, config: Config, deployer: Deployer):
    authz = request.headers.get("authorization")
    if authz is None or not authz.lower().startswith("bearer "):
        return text_response("Missing auth", 401)
    token = authz[7:]
    if token not in config.valid_tokens:
        return text_response("Token not found", 401)

    current_app.logger.info("Process pid: {}".format(os.getpid()))

    if request.content_length is None or request.content_length == 0:
        return text_response("Missing contents\n", 400)

    if request.content_type != "application/json":
        return text_response("Expected content type of application/json\n", 400)

    try:
        body = request.get_json()
    except BadRequest:
        return text_response("Invalid JSON", 400)

    current_app.logger.info("Received data: {}".format(body))

    try:
        model = DeployRequest.model_validate(body)
    except ValidationError as e:
        current_app.logger.info(f"Invalid model: {e}")
        return text_response("Invalid model", 400)

    if model.service not in config.services:
        return text_response("Unknown service", 400)

    service = config.services[model.service]

    for key in model.attributes.keys():
        if key not in service.mappings:
            return text_response(f"Unknown attribute: '{key}'", 400)

    with service_locks.hold_lock("test"):
        deployer.handle(
            service=service,
            attributes=model.attributes,
            force_deploy=model.forceDeploy or len(model.attributes) == 0,
        )

    return text_response("OK\n", 200)


@api.route("/")
def hello():
    return "https://github.com/blindern/deployer"
