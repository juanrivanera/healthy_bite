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

clientes_bp = Blueprint("clientes", __name__)


@clientes_bp.route("/elegir_plan/<int:plan_id>")
def elegir_plan(plan_id):
    if session.get("tipo") != "cliente":
        flash("Tenés que iniciar sesión como cliente para elegir un plan.")
        return redirect(url_for("auth.login_cliente"))

    cliente_id = session.get("cliente_id")
    if not cliente_id:
        flash("No se encontró el cliente en sesión.")
        return redirect(url_for("auth.login_cliente"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE cliente SET plan_id = ? WHERE id = ?", (plan_id, cliente_id))
    conn.commit()
    conn.close()

    flash("Plan actualizado correctamente.")
    return redirect(url_for("clientes.menu_cliente"))


@clientes_bp.route("/menu_cliente", methods=["GET", "POST"])
def menu_cliente():
    if session.get("tipo") != "cliente":
        flash("Tenés que iniciar sesión como cliente para ver esta página.")
        return redirect(url_for("auth.login_cliente"))

    cliente_id = session.get("cliente_id")
    if not cliente_id:
        flash("Sesión de cliente inválida.")
        return redirect(url_for("auth.login_cliente"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        disciplina = request.form.get("disciplina", "").strip()
        altura = request.form.get("altura", "").strip()
        peso = request.form.get("peso", "").strip()
        objetivo = request.form.get("objetivo", "").strip()

        try:
            altura_val = float(altura) if altura else None
        except ValueError:
            altura_val = None

        try:
            peso_val = float(peso) if peso else None
        except ValueError:
            peso_val = None

        cur.execute(
            """
            UPDATE cliente
            SET disciplina = ?, altura = ?, peso = ?, objetivo = ?
            WHERE id = ?
            """,
            (disciplina or None, altura_val, peso_val, objetivo or None, cliente_id),
        )
        conn.commit()
        flash("Datos actualizados correctamente.")

    cur.execute(
        """
        SELECT c.id,
               c.nombre,
               c.email,
               c.disciplina,
               c.altura,
               c.peso,
               c.objetivo,
               p.nombre AS plan
        FROM cliente c
        LEFT JOIN plan p ON c.plan_id = p.id
        WHERE c.id = ?
        """,
        (cliente_id,),
    )
    cliente = cur.fetchone()
    conn.close()

    if cliente is None:
        flash("Cliente no encontrado.")
        return redirect(url_for("auth.login_cliente"))

    return render_template("menu_cliente.html", cliente=cliente)


@clientes_bp.route("/pedidos_cliente", methods=["GET", "POST"])
def pedidos_cliente():
    if session.get("tipo") != "cliente":
        flash("No tenés permisos para ver tus pedidos.")
        return redirect(url_for("main.home"))

    cliente_id = session.get("cliente_id")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        plato_id = request.form.get("plato_id")
        restriccion = request.form.get("restriccion", "").strip()
        comentarios = request.form.get("comentarios", "").strip()

        if not plato_id:
            flash("Debés seleccionar un plato.")
        else:
            fecha_hoy = date.today().isoformat()
            cur.execute(
                """
                INSERT INTO pedido (cliente_id, plato_id, restriccion, comentarios, fecha)
                VALUES (?, ?, ?, ?, ?)
                """,
                (cliente_id, plato_id, restriccion, comentarios, fecha_hoy),
            )
            conn.commit()
            flash("Pedido creado correctamente.")

    cur.execute("SELECT * FROM plato ORDER BY id")
    platos = cur.fetchall()

    cur.execute(
        """
        SELECT p.id, pl.nombre AS plato, p.restriccion, p.comentarios, p.fecha, p.estado
        FROM pedido p
        JOIN plato pl ON p.plato_id = pl.id
        WHERE p.cliente_id = ?
        ORDER BY p.fecha DESC, p.id DESC
        """,
        (cliente_id,),
    )
    pedidos = cur.fetchall()

    conn.close()
    return render_template("pedidos_cliente.html", platos=platos, pedidos=pedidos)


@clientes_bp.route("/mis_recomendaciones")
def mis_recomendaciones():
    if session.get("tipo") != "cliente":
        flash("Tenés que iniciar sesión como cliente para ver tus recomendaciones.")
        return redirect(url_for("auth.login_cliente"))

    cliente_id = session.get("cliente_id")
    if not cliente_id:
        flash("Sesión de cliente inválida.")
        return redirect(url_for("auth.login_cliente"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.id,
               r.texto,
               r.fecha,
               n.nombre AS nutricionista
        FROM recomendacion r
        LEFT JOIN nutricionista n ON r.nutricionista_id = n.id
        WHERE r.cliente_id = ?
        ORDER BY r.fecha DESC, r.id DESC
        """,
        (cliente_id,),
    )
    recomendaciones = cur.fetchall()
    conn.close()

    return render_template("mis_recomendaciones.html", recomendaciones=recomendaciones)
