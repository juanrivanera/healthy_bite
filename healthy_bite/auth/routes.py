import os
import requests
from google_auth_oauthlib.flow import Flow
import sqlite3

from dotenv import load_dotenv 

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from healthy_bite.db import get_db

load_dotenv()

auth_bp = Blueprint("auth", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:5000/login_google/callback"
)

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


def _get_google_flow(state=None):
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [GOOGLE_REDIRECT_URI],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=GOOGLE_SCOPES,
        state=state,
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow


@auth_bp.route("/registro_cliente", methods=["GET", "POST"])
def registro_cliente():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM plan ORDER BY id")
    planes = cur.fetchall()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        disciplina = request.form.get("disciplina", "").strip()
        plan_id = request.form.get("plan_id", "").strip()
        altura = request.form.get("altura", "").strip()
        peso = request.form.get("peso", "").strip()
        objetivo = request.form.get("objetivo", "").strip()

        if not nombre or not email or not password or not plan_id:
            flash("Nombre, email, contraseña y plan son obligatorios.")
            conn.close()
            return render_template("registro_cliente.html", planes=planes)

        try:
            altura_val = float(altura) if altura else None
        except ValueError:
            altura_val = None

        try:
            peso_val = float(peso) if peso else None
        except ValueError:
            peso_val = None

        try:
            cur.execute(
                """
                INSERT INTO cliente (nombre, email, password, disciplina, plan_id, altura, peso, objetivo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (nombre, email, password, disciplina, plan_id, altura_val, peso_val, objetivo),
            )
            conn.commit()
            flash("Cliente registrado correctamente. Ya podés iniciar sesión.")
            return redirect(url_for("auth.login_cliente"))
        except sqlite3.IntegrityError:
            flash("Ya existe un cliente con ese email.")
            conn.close()
            return render_template("registro_cliente.html", planes=planes)

    conn.close()
    return render_template("registro_cliente.html", planes=planes)


@auth_bp.route("/registro_nutricionista", methods=["GET", "POST"])
def registro_nutricionista():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        matricula = request.form.get("matricula", "").strip()

        if not nombre or not email or not password or not matricula:
            flash("Todos los campos son obligatorios.")
            return render_template("registro_nutricionista.html")

        try:
            cur.execute(
                """
                INSERT INTO nutricionista (nombre, email, password, matricula)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, email, password, matricula),
            )
            conn.commit()
            flash("Nutricionista registrado correctamente. Ya podés iniciar sesión.")
            return redirect(url_for("auth.login_nutricionista"))
        except sqlite3.IntegrityError:
            flash("Ya existe un nutricionista con ese email.")
            return redirect(url_for("auth.registro_nutricionista"))
        finally:
            conn.close()

    return render_template("registro_nutricionista.html")


@auth_bp.route("/login_cliente", methods=["GET", "POST"])
def login_cliente():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM cliente WHERE email = ? AND password = ?",
            (email, password),
        )
        cli = cur.fetchone()
        conn.close()

        if cli is None:
            flash("Datos incorrectos.")
            return redirect(url_for("auth.login_cliente"))

        session.clear()
        session["tipo"] = "cliente"
        session["cliente_id"] = cli["id"]
        session["cliente_nombre"] = cli["nombre"]
        session["cliente_email"] = cli["email"]

        return redirect(url_for("clientes.menu_cliente"))

    return render_template("login_cliente.html")


@auth_bp.route("/login_nutricionista", methods=["GET", "POST"])
def login_nutricionista():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM nutricionista WHERE email = ? AND password = ?",
            (email, password),
        )
        nutri = cur.fetchone()
        conn.close()

        if nutri is None:
            flash("Datos incorrectos.")
            return redirect(url_for("auth.login_nutricionista"))

        session.clear()
        session["tipo"] = "nutricionista"
        session["nutricionista_id"] = nutri["id"]
        session["nutricionista_nombre"] = nutri["nombre"]

        return redirect(url_for("nutricionistas.menu_nutricionista"))

    return render_template("login_nutricionista.html")


@auth_bp.route("/login_google")
def login_google():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    flow = _get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    session["google_oauth_state"] = state
    return redirect(authorization_url)


@auth_bp.route("/login_google/callback")
def login_google_callback():
    state = session.get("google_oauth_state")

    if not state:
        flash("Sesión de Google inválida. Probá de nuevo.")
        return redirect(url_for("auth.login_cliente"))

    flow = _get_google_flow(state=state)
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=10,
    )

    if not resp.ok:
        flash("No se pudo obtener la información de Google.")
        return redirect(url_for("auth.login_cliente"))

    data = resp.json()
    email = data.get("email")
    nombre = data.get("name") or (email.split("@")[0] if email else "Cliente Google")

    if not email:
        flash("Google no devolvió un email válido.")
        return redirect(url_for("auth.login_cliente"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, nombre FROM cliente WHERE email = ?", (email,))
    row = cur.fetchone()

    if row is None:
        try:
            cur.execute(
                """
                INSERT INTO cliente (nombre, email, password)
                VALUES (?, ?, ?)
                """,
                (nombre, email, "google_oauth"),
            )
            conn.commit()
            cliente_id = cur.lastrowid
            cliente_nombre = nombre
        except sqlite3.IntegrityError:
            cur.execute("SELECT id, nombre FROM cliente WHERE email = ?", (email,))
            row = cur.fetchone()
            cliente_id = row["id"]
            cliente_nombre = row["nombre"]
    else:
        cliente_id = row["id"]
        cliente_nombre = row["nombre"]

    conn.close()

    session.clear()
    session["tipo"] = "cliente"
    session["cliente_id"] = cliente_id
    session["cliente_nombre"] = cliente_nombre
    session["cliente_email"] = email

    flash("Inicio de sesión con Google exitoso.")
    return redirect(url_for("clientes.menu_cliente"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for("main.home"))
