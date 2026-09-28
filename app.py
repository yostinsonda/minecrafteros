from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a MySQL (Actividad 2)
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',         # Cambia según tu usuario de MySQL
        password='yxz_sond4',         # Cambia según tu contraseña de MySQL
        database='cafeteria_universitaria'
    )
    return connection

# Actividad 3: Página Principal
@app.route('/')
def index():
    return render_template('index.html')

# Actividad 4: Mostrar Productos
@app.route('/productos')
def productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Consulta a la tabla producto
    cursor.execute("SELECT id_producto, nombre, categoria, precio, stock FROM producto;")
    productos_lista = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('productos.html', productos=productos_lista)

# Actividad 5: Mostrar Pedidos y Calcular Totales
@app.route('/pedidos')
def pedidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Consulta SQL con JOIN y SUM para relacionar las tablas y calcular el total
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

if __name__ == '__main__':
    app.run(debug=True)