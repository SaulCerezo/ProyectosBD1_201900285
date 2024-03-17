import mysql.connector


class CConexion:
    def ConexionBaseDatos():
        try:
            conexion = mysql.connector.connect(user='root',password='usac201900285@',
                                                host='127.0.0.1',
                                                database='proyectouno', port='3306')
            print("Conexion Correcta")
            return conexion

        except mysql.connector.Error as error:
            print("Error de conexion con la base de datos {}".format(error))
            return conexion
        

    ConexionBaseDatos()