from flask import Blueprint
__author__ = 'py'

boss = Blueprint('boss', __name__)

from . import views