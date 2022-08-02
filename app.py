# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import sys

from flask import Flask, render_template
from flask_babel import Babel
from flask_migrate import Migrate
from flask_mail import Mail

from hashkart.settings import Config
from hashkart.utils import log_slow_queries, jinja_global_varibles

from hashkart.user import views as account_view
from hashkart.checkout import views as checkout_view
from hashkart.discount import views as discount_view
from hashkart.product import views as product_view
from hashkart.order import views as order_view
from hashkart.api import api as api_view

babel = Babel()
migrate = Migrate()
mail = Mail()

def create_app(config_object=Config):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    jinja_global_varibles(app)
    log_slow_queries(app)
    return app

def register_extensions(app):
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)


def register_blueprints(app):
    app.pluggy.hook.flaskshop_load_blueprints(app=app)


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"errors/{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)


