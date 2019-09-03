import logging

from loguru import logger
from flask.logging import default_handler

from baldrick import github  # noqa

__all__ = ['create_app', '__version__']

__version__ = '0.3.dev0'

GLOBAL_TOML = ''


class InterceptHandler(logging.Handler):
    log_level_to_name = {5: 'TRACE',
                         10: 'DEBUG',
                         20: 'INFO',
                         25: 'SUCCESS',
                         30: 'WARNING',
                         40: 'ERROR',
                         50: 'CRITICAL'}

    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(self.log_level_to_name.get(record.levelno, record.levelno), record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)


def _init_global_toml():
    import os
    global GLOBAL_TOML

    GLOBAL_TOML = os.path.join('.', 'pyproject.toml')


def create_app(name, register_blueprints=True):
    """
    Create a flask app based on Baldrick.

    Parameters
    ----------
    name : `str`
        The name to be passed to ``Flask``. This will also be used as the bot
        user name. This can be overridden with ``app.bot_username``.

    register_blueprints : `bool`
        Register the default blueprints included with Baldrick.

    Returns
    -------
    app

    """
    import os

    from flask import Flask

    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
    except ImportError:
        from werkzeug.contrib.fixers import ProxyFix

    from baldrick.config import load, Config
    from baldrick.blueprints import github_blueprint, circleci_blueprint

    app = Flask(name)
    app.logger.removeHandler(default_handler)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Check if there is a global configuration
    if os.path.exists(GLOBAL_TOML):
        app.conf = load(GLOBAL_TOML, tool=name)
    else:
        app.conf = Config()

    app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
    app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']

    app.bot_username = name

    if register_blueprints:
        app.register_blueprint(github_blueprint)
        app.register_blueprint(circleci_blueprint)

    @app.route("/")
    def index():
        return "Nothing to see here"

    @app.route("/installation_authorized")
    def installation_authorized():
        return "Installation authorized"

    return app


_init_global_toml()
