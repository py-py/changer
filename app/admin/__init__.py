from flask import Blueprint
__author__ = 'py'

admin = Blueprint('admin', __name__)

from . import views