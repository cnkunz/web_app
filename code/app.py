from sqlalchemy import create_engine

mysql_conn_str = "mysql+pymysql://root:dev@productdb:3306/product"

engine = create_engine(mysql_conn_str)

connection = engine.connect()

q = connection.execute('SHOW DATABASES')

available_tables = q.fetchall()

print(available_tables)