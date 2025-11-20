from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from datetime import date

from healthy_bite.db import get_db

nutricionistas_bp = Blueprint("nutricionistas", __name__)


@nutricionistas_bp.route("/menu_nutricionista")
def menu_nutricionista():
    if session.get("tipo") != "nutricionista":
        flash("No tenés permisos para ver este menú.")
        return redirect(url_for("main.home"))

    return render_template("menu_nutricionista.html")


@nutricionistas_bp.route("/gestion_platos", methods=["GET", "POST"])
def gestion_platos():
    if session.get("tipo") != "nutricionista":
        flash("Solo los nutricionistas pueden gestionar los platos.")
        return redirect(url_for("main.home"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("SELECT id FROM plato ORDER BY id")
        ids = [row["id"] for row in cur.fetchall()]

        for pid in ids:
            nombre = request.form.get(f"nombre_{pid}", "").strip()
            descripcion = request.form.get(f"descripcion_{pid}", "").strip()

            if nombre:
                cur.execute(
                    "UPDATE plato SET nombre = ?, descripcion = ? WHERE id = ?",
                    (nombre, descripcion, pid),
                )

        conn.commit()
        flash("Platos actualizados correctamente.")

    cur.execute("SELECT * FROM plato ORDER BY id")
    platos = cur.fetchall()

    conn.close()
    return render_template("gestion_platos.html", platos=platos)


@nutricionistas_bp.route("/gestion_planes", methods=["GET", "POST"])
def gestion_planes():
    if session.get("tipo") != "nutricionista":
        flash("Solo los nutricionistas pueden gestionar los planes.")
        return redirect(url_for("main.home"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("SELECT id FROM plan ORDER BY id")
        ids = [r["id"] for r in cur.fetchall()]

        for pid in ids:
            nombre = request.form.get(f"nombre_plan_{pid}", "").strip()
            descripcion = request.form.get(f"descripcion_plan_{pid}", "").strip()
            precio = request.form.get(f"precio_plan_{pid}", "").strip()

            if nombre and descripcion and precio:
                try:
                    precio_val = float(precio)
                except ValueError:
                    continue
                cur.execute(
                    "UPDATE plan SET nombre = ?, descripcion = ?, precio = ? WHERE id = ?",
                    (nombre, descripcion, precio_val, pid),
                )

        conn.commit()
        flash("Planes actualizados correctamente.")

    cur.execute("SELECT * FROM plan ORDER BY id")
    planes = cur.fetchall()

    conn.close()
    return render_template("gestion_planes.html", planes=planes)


@nutricionistas_bp.route("/pedidos_nutricionista", methods=["GET", "POST"])
def pedidos_nutricionista():
    if session.get("tipo") != "nutricionista":
        flash("Solo los nutricionistas pueden ver los pedidos.")
        return redirect(url_for("main.home"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        pedido_id = request.form.get("pedido_id")

        if pedido_id:
            cur.execute(
                "UPDATE pedido SET estado = 'Validado' WHERE id = ?",
                (pedido_id,),
            )
            conn.commit()
            flash("Estado del pedido actualizado.")

    cur.execute(
        """
        SELECT p.id, c.nombre AS cliente, pl.nombre AS plato,
               p.restriccion, p.comentarios, p.fecha, p.estado
        FROM pedido p
        JOIN cliente c ON p.cliente_id = c.id
        JOIN plato pl ON p.plato_id = pl.id
        ORDER BY p.fecha DESC, p.id DESC
        """
    )
    pedidos = cur.fetchall()

    conn.close()
    return render_template("pedidos_nutricionista.html", pedidos=pedidos)


@nutricionistas_bp.route("/mis_recomendaciones")
def mis_recomendaciones():
    if session.get("tipo") != "nutricionista":
        flash("Solo los nutricionistas pueden ver sus recomendaciones.")
        return redirect(url_for("main.home"))

    nutricionista_id = session.get("nutricionista_id")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.id, c.nombre AS cliente, r.texto, r.fecha
        FROM recomendacion r
        JOIN cliente c ON r.cliente_id = c.id
        WHERE r.nutricionista_id = ?
        ORDER BY r.fecha DESC, r.id DESC
        """,
        (nutricionista_id,),
    )
    recomendaciones = cur.fetchall()
    conn.close()

    return render_template("mis_recomendaciones.html", recomendaciones=recomendaciones)


@nutricionistas_bp.route("/info_clientes")
def info_clientes():
    if session.get("tipo") != "nutricionista":
        flash("Solo los nutricionistas pueden ver la información de los clientes.")
        return redirect(url_for("main.home"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.nombre, c.email, c.disciplina, c.altura, c.peso, c.objetivo,
               p.nombre AS plan
        FROM cliente c
        LEFT JOIN plan p ON c.plan_id = p.id
        ORDER BY c.nombre
        """
    )
    clientes = cur.fetchall()
    conn.close()

    return render_template("info_clientes.html", clientes=clientes)


@nutricionistas_bp.route("/recomendar/<int:cliente_id>", methods=["GET", "POST"])
def recomendar(cliente_id):
    if session.get("tipo") != "nutricionista":
        flash("Solo los nutricionistas pueden crear recomendaciones.")
        return redirect(url_for("main.home"))

    nutricionista_id = session.get("nutricionista_id")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        texto = request.form.get("texto", "").strip()

        if not texto:
            flash("La recomendación no puede estar vacía.")
        else:
            fecha_hoy = date.today().isoformat()
            cur.execute(
                """
                INSERT INTO recomendacion (nutricionista_id, cliente_id, texto, fecha)
                VALUES (?, ?, ?, ?)
                """,
                (nutricionista_id, cliente_id, texto, fecha_hoy),
            )
            conn.commit()
            flash("Recomendación creada correctamente.")
            conn.close()
            return redirect(url_for("nutricionistas.menu_nutricionista"))

    cur.execute("SELECT nombre FROM cliente WHERE id = ?", (cliente_id,))
    cli = cur.fetchone()
    conn.close()

    if cli is None:
        flash("Cliente no encontrado.")
        return redirect(url_for("nutricionistas.info_clientes"))

    return render_template("recomendar.html", cliente=cli, cliente_id=cliente_id)
