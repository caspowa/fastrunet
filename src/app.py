from flask import Flask
from flask.ext.mongoengine import MongoEngine

from views import init_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object('settings')

    MongoEngine(app)

    init_routes(app)

    return app
