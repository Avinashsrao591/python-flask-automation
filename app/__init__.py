
from flask import Flask

from app.routes import main
from app.job_routes import jobs_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    app.register_blueprint(jobs_bp)
    return app
