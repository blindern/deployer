import logging
import sys

from flask import Flask, has_request_context, request
from flask_injector import FlaskInjector
from injector import Injector

from deployer.api import api


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        RequestFormatter(
            "[%(asctime)s] %(remote_addr)s %(levelname)s %(name)s %(message)s"
        )
    )

    root = logging.getLogger()
    root.addHandler(handler)

    logging.getLogger("deployer").setLevel(logging.DEBUG)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def create_app(injector: Injector):
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.register_blueprint(api)

    FlaskInjector(app=app, injector=injector)

    return app
