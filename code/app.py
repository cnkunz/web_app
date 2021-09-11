from sqlalchemy import create_engine

from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as ps
import ast

app = Flask(__name__)
api = Api(app)

class Orders(Resource):
    # methods go here
    pass

class Product(Resource):
    def get(self):
        data = GetProducts()
        data = data.to_dict()
        return {'data': data }, 200

api.add_resource(Orders, '/orders')  # '/users' is our entry point for Users
api.add_resource(Product, '/product')  # and '/locations' is our entry point for Locations

if __name__ == '__main__':
    app.run()



def GetProducts():
    mysql_conn_str = "mysql+pymysql://root:dev@db:3306/product"
    engine = create_engine(mysql_conn_str)
    connection = engine.connect()
    q = connection.execute('SHOW DATABASES')
    available_tables = q.fetchall()


    return available_tables