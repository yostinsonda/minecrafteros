from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',         
        password='yxz_sond4',         
        database='cafeteria_universitaria'
    )

# --- RUTAS PRINCIPALES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/productos')
def productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_producto, nombre, categoria, precio, stock FROM producto;")
    productos_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('productos.html', productos=productos_lista)

@app.route('/pedidos')
def pedidos():
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
    return render_template('pedidos.html', pedidos=pedidos_lista)


# --- SECCIÓN PRODUCTOS ---

@app.route('/Agregar_producto', methods=['GET', 'POST'])
def Agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO producto (nombre, categoria, precio, stock) VALUES (%s, %s, %s, %s)",
            (nombre, categoria, precio, stock)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/productos')
    
    return render_template('agregar_producto.html')


@app.route('/Actualizar_producto/<int:id>', methods=['GET', 'POST'])
def Actualizar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']

        cursor.execute(
            "UPDATE producto SET nombre = %s, categoria = %s, precio = %s, stock = %s WHERE id_producto = %s",
            (nombre, categoria, precio, stock, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/productos')

    cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
    prod = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_producto.html', producto=prod)


@app.route('/Borrar_producto/<int:id>')
def Borrar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/productos')


# --- SECCIÓN PEDIDOS ---

@app.route('/Agregar_pedido', methods=['GET', 'POST'])
def Agregar_pedido():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        fecha = request.form['fecha']
        id_cliente = request.form['id_cliente']
        estado = request.form['estado']

        cursor.execute(
            "INSERT INTO pedido (fecha_pedido, id_cliente, estado) VALUES (%s, %s, %s)",
            (fecha, id_cliente, estado)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/pedidos')

    cursor.execute("SELECT id_cliente, nombre FROM clientes")
    clientes_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('agregar_pedido.html', clientes=clientes_lista)


@app.route('/Actualizar_pedido/<int:id>', methods=['GET', 'POST'])
def Actualizar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        estado = request.form['estado']
        cursor.execute("UPDATE pedido SET estado = %s WHERE idpedido = %s", (estado, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/pedidos')

    cursor.execute("SELECT * FROM pedido WHERE idpedido = %s", (id,))
    ped = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_pedido.html', pedido=ped)


@app.route('/Borrar_pedido/<int:id>')
def Borrar_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Eliminamos el detalle del pedido primero por tema de llaves foráneas
    cursor.execute("DELETE FROM detalle_pedido WHERE id_pedido = %s", (id,))
    cursor.execute("DELETE FROM pedido WHERE idpedido = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/pedidos')


if __name__ == '__main__':
    app.run(debug=True)