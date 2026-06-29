from database.db_connection import conectar,cerrar_conexion

conn = conectar()
print("Conexión exitosa")
cerrar_conexion(conn)