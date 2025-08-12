from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint("main", __name__)

@bp.get("/")
@login_required
def index():
    return render_template("index.html", user=current_user)
