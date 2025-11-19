from flask import Flask
import os

from .db import init_db


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "hb2025"

    from .main.routes import main_bp
    from .auth.routes import auth_bp
    from .clientes.routes import clientes_bp
    from .nutricionistas.routes import nutricionistas_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(nutricionistas_bp)

    with app.app_context():
        init_db()

    @app.errorhandler(404)
    def page_not_found(e):
        return (
            "<h1>404 - Página no encontrada</h1><p>La página que buscás no existe.</p>",
            404,
        )

    return app
