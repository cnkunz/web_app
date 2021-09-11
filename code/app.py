from typing import Counter
from flask import Flask
from flask import jsonify, request
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


# Database functions
def GetAllProduct(query):
    mydict = create_dict()
    select_stuff = query
    cursor = conn.cursor()
    cursor.execute(select_stuff)
    result = cursor.fetchall()

    for row in result:
        mydict.add(row[0],({"item":row[0],"stock":row[1],"sold":row[2]}))

    stud_json = jsonify(mydict)

    return stud_json

def GetStock(item):
    
    mydict = create_dict()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM laptops WHERE item=" + f'"{item}"')
    result = cursor.fetchall()

    stock = [res[0] for res in result]

    return stock

def AddProduct(item, stock, sold):
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `laptops` (`item`, `stock`, `sold`) VALUES (" + f'"{item}"' + ", " + stock + ", " + sold + ")")

def removeFromStock(item):

    current = GetStock(item)
    new = current[0] - 1

    cursor = conn.cursor()
    cursor.execute("UPDATE laptops SET stock=" + str(new) + " WHERE item=" + f'"{item}"')

## Endpoints ##
class Orders(Resource):
    def get(self):
        
        data = GetStock("""SELECT item, sold FROM laptops""")
        return data

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('item', required=True)  # add args
        parser.add_argument('item-quantity', required=True)
        parser.add_argument('memory', required=True)
        parser.add_argument('memory-quatity')
        args = parser.parse_args()  # parse arguments to dictionary

        get_item = GetStock(str(args['item']))
        get_memory = GetStock(str(args['memory']))


        if get_item[0] < args['item-quantity']:
            color_out_of_stock = str(args['item'] + " is out of stock.")
            return color_out_of_stock
        elif get_memory[0] < args['memory-quanitity']:
            memory_out_of_stock = str(args['memory'] + " is out of stock.")
            return memory_out_of_stock
        else: 
            removeFromStock(str(args['item']), args['item-quantity'])
            removeFromStock(str(args['memory'], args['memory-quantity']))


class Product(Resource):

    def get(self):

        data = GetAllProduct("""SELECT * FROM laptops""")
        return data

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('item', required=True)  # add args
        parser.add_argument('stock', required=True)
        parser.add_argument('sold', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        AddProduct(args['item'], str(args['stock']), str(args['sold']))

        return GetAllProduct("""SELECT * FROM laptops""")





api.add_resource(Orders, '/orders')
api.add_resource(Product, '/product')


if __name__ == '__main__':
    app.run(host='0.0.0.0')