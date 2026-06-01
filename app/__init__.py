from flask import Flask
from config import Config


def create_app(config_object=None):
    app = Flask(__name__)

    if isinstance(config_object, dict):
        app.config.from_object(Config)
        app.config.update(config_object)
    else:
        app.config.from_object(config_object or Config)

    # Blueprints se registran en fases siguientes
    return app
