from flask import Blueprint
from pluggy import HookimplMarker

from .models import *

impl = HookimplMarker("hashkart")


@impl
def hashkart_load_blueprints(app):
    discount = Blueprint("discount", __name__)
    app.register_blueprint(discount, url_prefix="/discount")
