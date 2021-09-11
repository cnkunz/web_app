from flask import Flask
from flask import jsonify
from flask_restful import Resource, Api, reqparse
import mysql.connector
import json

app = Flask(__name__)
api = Api(app)

## MySQL connection ##
conn = mysql.connector.connect(user='root', password='dev', host='db', database='product')

if conn:
    print('works')
else:
    print('fuck')

class create_dict(dict):

    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value


def GetProduct(query):
    mydict = create_dict()
    select_stuff = query
    cursor = conn.cursor()
    cursor.execute(select_stuff)
    result = cursor.fetchall()

    for row in result:
        mydict.add(row[0],({"item":row[0],"stock":row[1],"sold":row[2]}))

    stud_json = jsonify(mydict)

    return stud_json

def GetStock(query):
    stock_query = query
    
    mydict = create_dict()
    cursor = conn.cursor()
    cursor.execute(stock_query)
    result = cursor.fetchall()

    for row in result:
        mydict.add(row[0],({"stock":row[0]}))

    stud_json = jsonify(mydict)

    return stud_json

## Endpoints ##
class Orders(Resource):
    def get(self):

        data = GetStock("""SELECT stock FROM laptops""")
        return data

class Product(Resource):

    def get(self):

        data = GetProduct("""SELECT * FROM laptops""")
        return data
#        return {'data': data }, 200

api.add_resource(Orders, '/orders')
api.add_resource(Product, '/product')


if __name__ == '__main__':
    app.run(host='0.0.0.0')