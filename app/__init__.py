from flask import Flask
from config import Config
from flask_apscheduler import APScheduler
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os
import warnings
warnings.filterwarnings("ignore")

scheduler = APScheduler()
cors = CORS()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    cors.init_app(app, supports_credentials=True)

    scheduler.init_app(app)
    scheduler.start()

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/LaiZhou.log', maxBytes=10240,
            backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('LaiZhou startup')   

    return app