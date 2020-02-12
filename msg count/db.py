from mysql.connector import (connection)

class Connect():
	def conn():
		try:
			mydb = connection.MySQLConnection(
				host="",
				user="",
				passwd="",
				database=""
				)

			return mydb
		except Exception as e:
			print("[ERR]Connection failed")
			print(f"[ERR]Error = {e}")
		