from flask import Flask, jsonify
import mysql.connector
import os
import csv
# Directorio donde se encuentran los archivos CSV
csv_directory = "C:/Users/Saul/Desktop/tablas/"

app = Flask(__name__)

# Configura la conexión a la base de datos MySQL
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'usac201900285@',
    'database': 'proyectouno'
}


# Función para eliminar todas las tablas de la base de datos
def eliminar_tablas():
    try:
        # Conecta a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Desactiva las restricciones de clave externa
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Obtiene la lista de todas las tablas en la base de datos
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Elimina cada tabla encontrada
        for table in tables:
            cursor.execute(f"DROP TABLE {table[0]}")

        # Activa las restricciones de clave externa nuevamente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Confirma los cambios y cierra la conexión
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return str(e)

# Función para crear las tablas en la base de datos
def crear_tablas():
    try:
        # Conecta a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Sentencia SQL para crear la tabla categoria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categoria (
                id_categoria INTEGER NOT NULL,
                nombre VARCHAR(25) NOT NULL,
                PRIMARY KEY (id_categoria)
            )
        """)

        # Sentencia SQL para crear la tabla producto
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS producto (
                id_producto INTEGER NOT NULL,
                nombre VARCHAR(50) NOT NULL,
                precio NUMERIC(6,2) NOT NULL,
                categoria_id_categoria INTEGER NOT NULL,
                PRIMARY KEY (id_producto),
                FOREIGN KEY (categoria_id_categoria) REFERENCES categoria (id_categoria)
            )
        """)

        # Sentencia SQL para crear la tabla pais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pais (
                id_pais INTEGER NOT NULL,
                nombre VARCHAR(50) NOT NULL,
                PRIMARY KEY (id_pais)
            )
        """)

        # Sentencia SQL para crear la tabla cliente
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                id_cliente INTEGER NOT NULL,
                nombre VARCHAR(15) NOT NULL,
                apellido VARCHAR(25) NOT NULL,
                direccion VARCHAR(100) NOT NULL,
                telefono VARCHAR(10) NOT NULL,
                tarjeta VARCHAR(20) NOT NULL,
                edad INTEGER NOT NULL,
                salario INTEGER NOT NULL,
                genero CHAR(1) NOT NULL,
                pais_id_pais INTEGER NOT NULL,
                PRIMARY KEY (id_cliente),
                FOREIGN KEY (pais_id_pais) REFERENCES pais (id_pais)
            )
        """)

        # Sentencia SQL para crear la tabla vendedor
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendedor (
                id_vendedor INTEGER NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                pais_id_pais INTEGER NOT NULL,
                PRIMARY KEY (id_vendedor),
                FOREIGN KEY (pais_id_pais) REFERENCES pais (id_pais)
            )
        """)

        # Sentencia SQL para crear la tabla orden
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orden (
                id_orden INTEGER AUTO_INCREMENT PRIMARY KEY,
                linea_orden INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                vendedor_id_vendedor INTEGER NOT NULL,
                producto_id_producto INTEGER NOT NULL,
                FOREIGN KEY (vendedor_id_vendedor) REFERENCES vendedor (id_vendedor),
                FOREIGN KEY (producto_id_producto) REFERENCES producto (id_producto)
            )
        """)

        # Sentencia SQL para crear la tabla detalle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle (
                id_detalle SERIAL PRIMARY KEY,
                fecha_orden VARCHAR(10) NOT NULL,
                cliente_id_cliente INTEGER NOT NULL,
                orden_id_orden INTEGER NOT NULL,
                id_orden_detalle INTEGER NOT NULL,
                CONSTRAINT unique_orden_cliente_fecha UNIQUE (orden_id_orden, fecha_orden, cliente_id_cliente),
                FOREIGN KEY (cliente_id_cliente) REFERENCES cliente (id_cliente),
                FOREIGN KEY (orden_id_orden) REFERENCES orden (id_orden)
            )
        """)


        # Confirma los cambios y cierra la conexión
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return str(e)

# Función para cargar datos desde archivos CSV a las tablas de la base de datos
def cargar_datos():
    try:
        # Conecta a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Lista de archivos CSV a cargar primero
        archivos_prioritarios = ["categoria.csv", "pais.csv", "cliente.csv", "vendedor.csv", "producto.csv"]

        # Itera sobre los archivos CSV prioritarios
        for filename in archivos_prioritarios:
            if filename in os.listdir(csv_directory):
                table_name = filename.split(".")[0]
                print(f"Cargando {table_name}...")
                with open(os.path.join(csv_directory, filename), 'r') as file:
                    csv_reader = csv.reader(file, delimiter=';')
                    next(csv_reader)  # Saltar la primera línea si contiene encabezados
                    for row in csv_reader:
                        cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['%s']*len(row))})", row)
                print(f"{table_name} cargado.")
        
        # Cargar los datos de la tabla "orden" en las tablas "orden" y "detalle"
        print("Cargando tabla 'orden'...")
        with open(os.path.join(csv_directory, "orden.csv"), 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader)  # Saltar la primera línea si contiene encabezados
            for row in csv_reader:
                # Extraer los datos relevantes para cada tabla
                id_orden, linea_orden, fecha_orden, id_cliente, id_vendedor, id_producto, cantidad = row

                # Insertar datos en la tabla "orden"
                cursor.execute("INSERT INTO orden (linea_orden, cantidad, vendedor_id_vendedor, producto_id_producto) VALUES (%s, %s, %s, %s)", (linea_orden, cantidad, id_vendedor, id_producto))

                # Obtener el ID de orden insertado
                last_order_id = cursor.lastrowid

                # Insertar datos en la tabla "detalle"
                cursor.execute("INSERT INTO detalle (fecha_orden, cliente_id_cliente, orden_id_orden, id_orden_detalle) VALUES (%s, %s, %s, %s)", (fecha_orden, id_cliente, last_order_id, id_orden))

        print("Datos cargados en 'orden' y 'detalle'.")

        # Confirma los cambios y cierra la conexión
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return str(e)

# Función para borrar toda la información de todas las tablas de la base de datos
def borrar_info_db():
    try:
        # Conecta a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Desactiva las restricciones de clave externa
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Obtiene la lista de todas las tablas en la base de datos
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Borra todas las filas de cada tabla
        for table in tables:
            cursor.execute(f"DELETE FROM {table[0]}")

        # Activa las restricciones de clave externa nuevamente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Confirma los cambios y cierra la conexión
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return str(e)


# Función para ejecutar la consulta y obtener el cliente que más ha comprado
def consultar_cliente_mas_compras():
    try:
        # Conecta a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Ejecuta la consulta
        cursor.execute("""
            SELECT c.id_cliente, c.nombre, c.apellido, p.nombre AS pais, SUM(o.cantidad) AS monto_total
            FROM cliente c
            JOIN detalle d ON c.id_cliente = d.cliente_id_cliente
            JOIN orden o ON d.orden_id_orden = o.id_orden
            JOIN pais p ON c.pais_id_pais = p.id_pais
            GROUP BY c.id_cliente
            ORDER BY SUM(o.cantidad) DESC
            LIMIT 1
        """)
        
        # Obtiene el resultado de la consulta
        resultado = cursor.fetchone()

        # Cierra la conexión a la base de datos
        cursor.close()
        conn.close()

        return resultado

    except Exception as e:
        return str(e)



# Función para obtener la información del producto más y menos comprado
def obtener_productos_mas_y_menos_comprados():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener el producto más comprado
    cursor.execute("""
        SELECT p.id_producto, p.nombre, c.nombre, SUM(o.cantidad) AS total_unidades, SUM(o.cantidad * p.precio) AS monto_vendido
        FROM producto p
        INNER JOIN orden o ON p.id_producto = o.producto_id_producto
        INNER JOIN categoria c ON p.categoria_id_categoria = c.id_categoria
        INNER JOIN detalle d ON o.id_orden = d.orden_id_orden
        INNER JOIN cliente cl ON d.cliente_id_cliente = cl.id_cliente
        GROUP BY p.id_producto
        ORDER BY total_unidades DESC
        LIMIT 1
    """)
    producto_mas_comprado = cursor.fetchone()

    # Consulta para obtener el producto menos comprado
    cursor.execute("""
        SELECT p.id_producto, p.nombre, c.nombre, SUM(o.cantidad) AS total_unidades, SUM(o.cantidad * p.precio) AS monto_vendido
        FROM producto p
        INNER JOIN orden o ON p.id_producto = o.producto_id_producto
        INNER JOIN categoria c ON p.categoria_id_categoria = c.id_categoria
        INNER JOIN detalle d ON o.id_orden = d.orden_id_orden
        INNER JOIN cliente cl ON d.cliente_id_cliente = cl.id_cliente
        GROUP BY p.id_producto
        ORDER BY total_unidades ASC
        LIMIT 1
    """)
    producto_menos_comprado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return producto_mas_comprado, producto_menos_comprado



# Función para obtener la información del vendedor que más ha vendido
def obtener_vendedor_mas_vendio():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener al vendedor que más ha vendido
    cursor.execute("""
        SELECT v.id_vendedor, v.nombre, SUM(o.cantidad * p.precio) AS monto_total_vendido
        FROM vendedor v
        INNER JOIN orden o ON v.id_vendedor = o.vendedor_id_vendedor
        INNER JOIN producto p ON o.producto_id_producto = p.id_producto
        GROUP BY v.id_vendedor
        ORDER BY monto_total_vendido DESC
        LIMIT 1
    """)
    vendedor_mas_vendio = cursor.fetchone()

    cursor.close()
    conexion.close()

    return vendedor_mas_vendio


# Función para obtener la información del país que más y menos ha vendido dentro del rango especificado
def obtener_paises_mas_y_menos_vendieron(rango_inicio, rango_fin):
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener el país que más ha vendido dentro del rango especificado
    cursor.execute("""
        SELECT p.nombre, SUM(o.cantidad * pr.precio) AS monto_total_vendido
        FROM pais p
        INNER JOIN cliente cl ON p.id_pais = cl.pais_id_pais
        INNER JOIN detalle d ON cl.id_cliente = d.cliente_id_cliente
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        GROUP BY p.nombre
        HAVING monto_total_vendido >= %s AND monto_total_vendido <= %s
        ORDER BY monto_total_vendido DESC
        LIMIT 1
    """, (rango_inicio, rango_fin))
    pais_mas_vendio = cursor.fetchone()

    # Consulta para obtener el país que menos ha vendido dentro del rango especificado
    cursor.execute("""
        SELECT p.nombre, SUM(o.cantidad * pr.precio) AS monto_total_vendido
        FROM pais p
        INNER JOIN cliente cl ON p.id_pais = cl.pais_id_pais
        INNER JOIN detalle d ON cl.id_cliente = d.cliente_id_cliente
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        GROUP BY p.nombre
        HAVING monto_total_vendido >= %s AND monto_total_vendido <= %s
        ORDER BY monto_total_vendido ASC
        LIMIT 1
    """, (rango_inicio, rango_fin))
    pais_menos_vendio = cursor.fetchone()

    cursor.close()
    conexion.close()

    return pais_mas_vendio, pais_menos_vendio


# Función para obtener el top 5 de países que más han comprado
def obtener_top5_paises_mas_compraron():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener el top 5 de países que más han comprado
    cursor.execute("""
        SELECT p.id_pais, p.nombre, SUM(o.cantidad * pr.precio) AS monto_total_vendido
        FROM pais p
        INNER JOIN cliente cl ON p.id_pais = cl.pais_id_pais
        INNER JOIN detalle d ON cl.id_cliente = d.cliente_id_cliente
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        GROUP BY p.id_pais, p.nombre
        ORDER BY monto_total_vendido ASC
        LIMIT 5
    """)
    top5_paises = cursor.fetchall()

    cursor.close()
    conexion.close()

    return top5_paises

# Función para obtener la información de la categoría que más y menos se ha comprado
def obtener_categorias_mas_y_menos_compradas():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener la categoría que más se ha comprado
    cursor.execute("""
        SELECT c.nombre, SUM(o.cantidad) AS total_unidades
        FROM categoria c
        INNER JOIN producto p ON c.id_categoria = p.categoria_id_categoria
        INNER JOIN orden o ON p.id_producto = o.producto_id_producto
        GROUP BY c.id_categoria
        ORDER BY total_unidades DESC
        LIMIT 1
    """)
    categoria_mas_comprada = cursor.fetchone()

    # Consulta para obtener la categoría que menos se ha comprado
    cursor.execute("""
        SELECT c.nombre, SUM(o.cantidad) AS total_unidades
        FROM categoria c
        INNER JOIN producto p ON c.id_categoria = p.categoria_id_categoria
        INNER JOIN orden o ON p.id_producto = o.producto_id_producto
        GROUP BY c.id_categoria
        ORDER BY total_unidades ASC
        LIMIT 1
    """)
    categoria_menos_comprada = cursor.fetchone()

    cursor.close()
    conexion.close()

    return categoria_mas_comprada, categoria_menos_comprada


# Función para obtener la categoría más comprada por cada país
def obtener_categorias_mas_compradas_por_pais():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener la categoría más comprada por cada país
    cursor.execute("""
        SELECT pa.id_pais, pa.nombre AS nombre_pais, c.nombre AS nombre_categoria, SUM(o.cantidad) AS total_unidades
        FROM pais pa
        INNER JOIN cliente cl ON pa.id_pais = cl.pais_id_pais
        INNER JOIN detalle d ON cl.id_cliente = d.cliente_id_cliente
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        INNER JOIN categoria c ON pr.categoria_id_categoria = c.id_categoria
        GROUP BY pa.id_pais, c.id_categoria
        ORDER BY pa.id_pais, total_unidades DESC
    """)

    resultados = cursor.fetchall()

    categorias_mas_compradas_por_pais = {}

    for fila in resultados:
        id_pais = fila[0]
        nombre_pais = fila[1]
        nombre_categoria = fila[2]
        total_unidades = fila[3]

        if id_pais not in categorias_mas_compradas_por_pais:
            categorias_mas_compradas_por_pais[id_pais] = {
                "nombre_pais": nombre_pais,
                "categoria_mas_comprada": {
                    "nombre_categoria": nombre_categoria,
                    "total_unidades": total_unidades
                }
            }
        else:
            # Si ya se ha encontrado una categoría más comprada para este país, comparamos las unidades
            # y actualizamos solo si las unidades de esta categoría son mayores
            if total_unidades > categorias_mas_compradas_por_pais[id_pais]["categoria_mas_comprada"]["total_unidades"]:
                categorias_mas_compradas_por_pais[id_pais]["categoria_mas_comprada"] = {
                    "nombre_categoria": nombre_categoria,
                    "total_unidades": total_unidades
                }

    cursor.close()
    conexion.close()

    return categorias_mas_compradas_por_pais


# Función para obtener las ventas por mes de Inglaterra
def obtener_ventas_por_mes_inglaterra():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener las ventas por mes de Inglaterra
    cursor.execute("""
        SELECT MONTH(STR_TO_DATE(d.fecha_orden, '%d/%m/%Y')) AS numero_mes, 
               SUM(o.cantidad * pr.precio) AS monto
        FROM pais pa
        INNER JOIN cliente cl ON pa.id_pais = cl.pais_id_pais
        INNER JOIN detalle d ON cl.id_cliente = d.cliente_id_cliente
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        WHERE pa.nombre = 'Inglaterra'
        GROUP BY numero_mes
        ORDER BY numero_mes
    """)

    ventas_por_mes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return ventas_por_mes


# Función para obtener el mes con más y menos ventas
def obtener_meses_max_min_ventas():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener el mes con más y menos ventas
    cursor.execute("""
        SELECT MONTH(STR_TO_DATE(d.fecha_orden, '%d/%m/%Y')) AS numero_mes, 
               SUM(o.cantidad * pr.precio) AS monto
        FROM detalle d
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        GROUP BY numero_mes
        ORDER BY monto DESC
        LIMIT 1
    """)
    mes_max_ventas = cursor.fetchone()

    cursor.execute("""
        SELECT MONTH(STR_TO_DATE(d.fecha_orden, '%d/%m/%Y')) AS numero_mes, 
               SUM(o.cantidad * pr.precio) AS monto
        FROM detalle d
        INNER JOIN orden o ON d.orden_id_orden = o.id_orden
        INNER JOIN producto pr ON o.producto_id_producto = pr.id_producto
        GROUP BY numero_mes
        ORDER BY monto ASC
        LIMIT 1
    """)
    mes_min_ventas = cursor.fetchone()

    cursor.close()
    conexion.close()

    return mes_max_ventas, mes_min_ventas

# Función para obtener las ventas de cada producto de la categoría "deportes"
def obtener_ventas_productos_deportes():
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()

    # Consulta para obtener las ventas de cada producto de la categoría "deportes"
    cursor.execute("""
        SELECT pr.id_producto, pr.nombre, SUM(o.cantidad * pr.precio) AS monto
        FROM producto pr
        INNER JOIN orden o ON pr.id_producto = o.producto_id_producto
        INNER JOIN detalle d ON o.id_orden = d.orden_id_orden
        INNER JOIN categoria c ON pr.categoria_id_categoria = c.id_categoria
        WHERE c.nombre = 'deportes'
        GROUP BY pr.id_producto
    """)
    ventas_productos_deportes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return ventas_productos_deportes

#########################################################################################
#                               ENDPOINTS                                               #
#########################################################################################

# Define el endpoint /eliminarmodelo
@app.route('/eliminarmodelo', methods=['DELETE'])
def eliminar_modelo():
    result = eliminar_tablas()
    if result == True:
        return "Todas las tablas fueron eliminadas exitosamente."
    else:
        return f"Error al eliminar las tablas: {result}", 500

# Define el endpoint /crearmodelo
@app.route('/crearmodelo', methods=['POST'])
def crear_modelo():
    result = crear_tablas()
    if result == True:
        return "Tablas creadas exitosamente."
    else:
        return f"Error al crear las tablas: {result}", 500


# Define el endpoint /cargarmodelo
@app.route('/cargarmodelo', methods=['POST'])
def cargar_modelo():
    result = cargar_datos()
    if result == True:
        return "Datos cargados exitosamente."
    else:
        return f"Error al cargar los datos: {result}", 500

# Define el endpoint /borrarinfodb
@app.route('/borrarinfodb', methods=['DELETE'])
def borrar_info():
    result = borrar_info_db()
    if result == True:
        return "Información de todas las tablas eliminada exitosamente."
    else:
        return f"Error al eliminar la información de las tablas: {result}", 500


# Define el endpoint "/consulta1"
@app.route('/consulta1')
def consulta1():
    cliente_mas_compras = consultar_cliente_mas_compras()
    if cliente_mas_compras:
        # Formatea el resultado como un JSON
        resultado_json = {
            'id_cliente': cliente_mas_compras[0],
            'nombre': cliente_mas_compras[1],
            'apellido': cliente_mas_compras[2],
            'pais': cliente_mas_compras[3],
            'monto_total': cliente_mas_compras[4]
        }
        return jsonify(resultado_json)
    else:
        return 'Error al consultar el cliente que más ha comprado'

# Ruta para el endpoint /consulta2
@app.route('/consulta2')
def consulta2():
    producto_mas_comprado, producto_menos_comprado = obtener_productos_mas_y_menos_comprados()

    respuesta = {
        "producto_mas_comprado": {
            "id_producto": producto_mas_comprado[0],
            "nombre_producto": producto_mas_comprado[1],
            "categoria": producto_mas_comprado[2],
            "total_unidades": producto_mas_comprado[3],
            "monto_vendido": producto_mas_comprado[4]
        },
        "producto_menos_comprado": {
            "id_producto": producto_menos_comprado[0],
            "nombre_producto": producto_menos_comprado[1],
            "categoria": producto_menos_comprado[2],
            "total_unidades": producto_menos_comprado[3],
            "monto_vendido": producto_menos_comprado[4]
        }
    }

    return jsonify(respuesta)


# Ruta para el endpoint /consulta3
@app.route('/consulta3')
def consulta3():
    vendedor_mas_vendio = obtener_vendedor_mas_vendio()

    respuesta = {
        "vendedor_con_mas_ventas": {
            "id_vendedor": vendedor_mas_vendio[0],
            "nombre_vendedor": vendedor_mas_vendio[1],
            "monto_total_vendido": vendedor_mas_vendio[2]
        }
    }

    return jsonify(respuesta)


# Ruta para el endpoint /consulta4
@app.route('/consulta4')
def consulta4():
    # Definir el rango de montos
    rango_inicio = 119000
    rango_fin = 318000

    pais_mas_vendio, pais_menos_vendio = obtener_paises_mas_y_menos_vendieron(rango_inicio, rango_fin)

    respuesta = {
        "pais_con_mas_ventas": {
            "nombre_pais": pais_mas_vendio[0],
            "monto_total_vendido": pais_mas_vendio[1]
        },
        "pais_con_menos_ventas": {
            "nombre_pais": pais_menos_vendio[0],
            "monto_total_vendido": pais_menos_vendio[1]
        }
    }

    return jsonify(respuesta)

# Ruta para el endpoint /consulta5
@app.route('/consulta5')
def consulta5():
    top5_paises = obtener_top5_paises_mas_compraron()

    respuesta = [{
        "id_pais": pais[0],
        "nombre_pais": pais[1],
        "monto_total_vendido": pais[2]
    } for pais in top5_paises]

    return jsonify(respuesta)


# Ruta para el endpoint /consulta6
@app.route('/consulta6')
def consulta6():
    categoria_mas_comprada, categoria_menos_comprada = obtener_categorias_mas_y_menos_compradas()

    respuesta = {
        "categoria_mas_comprada": {
            "nombre_categoria": categoria_mas_comprada[0],
            "total_unidades": categoria_mas_comprada[1]
        },
        "categoria_menos_comprada": {
            "nombre_categoria": categoria_menos_comprada[0],
            "total_unidades": categoria_menos_comprada[1]
        }
    }

    return jsonify(respuesta)

# Ruta para el endpoint /consulta7
@app.route('/consulta7')
def consulta7():
    categorias_mas_compradas_por_pais = obtener_categorias_mas_compradas_por_pais()

    respuesta = [categorias_mas_compradas_por_pais[pais] for pais in categorias_mas_compradas_por_pais]

    return jsonify(respuesta)

# Ruta para el endpoint /consulta8
@app.route('/consulta8')
def consulta8():
    ventas_por_mes = obtener_ventas_por_mes_inglaterra()

    respuesta = [{
        "numero_mes": venta[0],
        "monto": float(venta[1])  # Convertir el monto a un número decimal
    } for venta in ventas_por_mes]

    return jsonify(respuesta)


# Ruta para el endpoint /consulta9
@app.route('/consulta9')
def consulta9():
    mes_max_ventas, mes_min_ventas = obtener_meses_max_min_ventas()

    respuesta = {
        "mes_max_ventas": {"numero_mes": mes_max_ventas[0], "monto": float(mes_max_ventas[1]) if mes_max_ventas else 0},
        "mes_min_ventas": {"numero_mes": mes_min_ventas[0], "monto": float(mes_min_ventas[1]) if mes_min_ventas else 0}
    }

    return jsonify(respuesta)

# Ruta para el endpoint /consulta10
@app.route('/consulta10')
def consulta10():
    ventas_productos_deportes = obtener_ventas_productos_deportes()

    respuesta = [{
        "id_producto": venta[0],
        "nombre": venta[1],
        "monto": float(venta[2])
    } for venta in ventas_productos_deportes]

    return jsonify(respuesta)


if __name__ == '__main__':
    app.run(debug=True)
