from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Función para conectar a la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='yxz_sond4',
        database='cafeteria_universitaria'
    )

@app.route("/")
def inicio():
    return render_template("index.html")  # O la plantilla principal que tengas
# ==========================================
# SECCIÓN PRODUCTOS
# ==========================================

@app.route("/productos")
def listar_productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_producto, nombre, categoria, precio, stock FROM producto;")
    productos_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("productos.html", productos=productos_lista)

@app.route("/Agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO producto (nombre, categoria, precio, stock) VALUES (%s, %s, %s, %s)",
            (nombre, categoria, precio, stock)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("listar_productos"))
    return render_template("agregar_producto.html")

@app.route("/buscar_actualizar_producto", methods=["POST"])
def buscar_actualizar_producto():
    id_prod = request.form.get("id_producto")
    if id_prod:
        return redirect(url_for("actualizar_producto", id=id_prod))
    return redirect(url_for("listar_productos"))

@app.route("/Actualizar_producto/<int:id>", methods=["GET", "POST"])
def actualizar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        cursor.execute(
            "UPDATE producto SET nombre=%s, categoria=%s, precio=%s, stock=%s WHERE id_producto=%s",
            (nombre, categoria, precio, stock, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("listar_productos"))

    cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
    prod = cursor.fetchone()
    cursor.close()
    conn.close()

    if not prod:
        return redirect(url_for("listar_productos"))

    return render_template("actualizar_producto.html", prod=prod)

@app.route("/Borrar_producto", methods=["POST"])
def borrar_producto():
    id_prod = request.form.get("id_producto")
    if id_prod:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id_prod,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for("listar_productos"))

# ==========================================
# SECCIÓN PEDIDOS
# ==========================================

@app.route("/pedidos")
def listar_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            p.idpedido,
            c.nombre AS cliente,
            p.fecha_pedido AS fecha,
            p.estado,
            IFNULL(SUM(dp.cantidad * dp.precio_unitario), 0) AS total
        FROM pedido p
        JOIN clientes c ON p.id_cliente = c.id_cliente
        LEFT JOIN detalle_pedido dp ON p.idpedido = dp.id_pedido
        GROUP BY p.idpedido, c.nombre, p.fecha_pedido, p.estado
        ORDER BY p.idpedido ASC;
    """
    cursor.execute(query)
    pedidos_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("pedidos.html", pedidos=pedidos_lista)

@app.route("/Agregar_pedido", methods=["GET", "POST"])
def agregar_pedido():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        fecha = request.form["fecha"]
        id_cliente = request.form["id_cliente"]
        estado = request.form["estado"]

        cursor.execute(
            "INSERT INTO pedido (fecha_pedido, id_cliente, estado) VALUES (%s, %s, %s)",
            (fecha, id_cliente, estado)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("listar_pedidos"))

    # Para el método GET: cargamos los clientes para llenar el desplegable <select>
    cursor.execute("SELECT id_cliente, nombre FROM clientes")
    clientes_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("agregar_pedido.html", clientes=clientes_lista)

@app.route("/buscar_actualizar_pedido", methods=["POST"])
def buscar_actualizar_pedido():
    id_ped = request.form.get("id_pedido")
    if id_ped:
        return redirect(url_for("actualizar_pedido", id=id_ped))
    return redirect(url_for("listar_pedidos"))

@app.route("/Actualizar_pedido/<int:id>", methods=["GET", "POST"])
def actualizar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        estado = request.form["estado"]
        cursor.execute("UPDATE pedido SET estado = %s WHERE idpedido = %s", (estado, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("listar_pedidos"))

    cursor.execute("SELECT * FROM pedido WHERE idpedido = %s", (id,))
    ped = cursor.fetchone()
    cursor.close()
    conn.close()

    if not ped:
        return redirect(url_for("listar_pedidos"))

    return render_template("actualizar_pedido.html", ped=ped)

@app.route("/Borrar_pedido", methods=["POST"])
def borrar_pedido():
    id_ped = request.form.get("id_pedido")
    if id_ped:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Se elimina primero en detalle_pedido por la restricción de clave foránea
        cursor.execute("DELETE FROM detalle_pedido WHERE id_pedido = %s", (id_ped,))
        cursor.execute("DELETE FROM pedido WHERE idpedido = %s", (id_ped,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for("listar_pedidos"))

if __name__ == "__main__":
    app.run(debug=True)