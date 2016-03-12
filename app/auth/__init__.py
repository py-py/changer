from flask import Blueprint
__author__ = 'py'

auth = Blueprint('auth', __name__)

from . import views