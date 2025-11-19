from flask import Blueprint, render_template
from healthy_bite.db import get_db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    conn = get_db()
    planes = conn.execute("SELECT * FROM plan").fetchall()
    conn.close()
    return render_template("home.html", planes=planes)


@main_bp.route("/planes")
def planes():
    conn = get_db()
    planes = conn.execute("SELECT * FROM plan").fetchall()
    conn.close()
    return render_template("planes.html", planes=planes)
