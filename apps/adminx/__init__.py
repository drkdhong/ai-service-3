#apps/adminx/__init__.py
from flask import Blueprint

adminx = Blueprint('adminx', __name__, template_folder='templates')

from . import views  # views.py import해서 라우팅 등록