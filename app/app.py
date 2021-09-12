from flask import Flask
from flask import jsonify
from flask_restful import Resource, Api, reqparse
import mysql.connector
import json

app = Flask(__name__)
api = Api(app)

c_laptop = 1000

## MySQL connection ##
conn = mysql.connector.connect(user='root', password='dev', host='db', database='product')

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
        mydict.add(row[0],({"item":row[0],"stock":row[1],"sold":row[2],"price":row[3]}))

    stud_json = jsonify(mydict)

    return stud_json

def GetOrders():

    cursor = conn.cursor()
    cursor.execute("SELECT item, sold FROM laptops")
    result = cursor.fetchall()

    return result

def GetStock(item):
    
    mydict = create_dict()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM laptops WHERE item=" + f'"{item}"')
    result = cursor.fetchall()

    stock = [res[0] for res in result]

    return stock

def GetSold(item):

    cursor = conn.cursor()
    cursor.execute("SELECT sold FROM laptops WHERE item=" + f'"{item}"')
    result = cursor.fetchall()

    sold = [res[0] for res in result]

    return sold

def AddProduct(item, stock, sold, price):
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `laptops` (`item`, `stock`, `sold`, `price`) VALUES (" + f'"{item}"' + ", " + stock + ", " + sold + "," + price + ")")
    conn.commit()

def UpdateProduct(item, stock, price):

    cursor = conn.cursor()
    cursor.execute("UPDATE laptops SET stock=" + stock + ", price=" + price + " WHERE item=" + f'"{item}"')
    conn.commit()

def removeFromStock(item, quant):

    cursor = conn.cursor()

    current = GetStock(item)
    new = current[0] - int(quant)

    cursor.execute("UPDATE laptops SET stock=" + str(new) + " WHERE item=" + f'"{item}"')
    conn.commit()

def GetPrice(memory):
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM laptops where item=" + f'"{memory}"')

    result = cursor.fetchall()

    price = [res[0] for res in result]

    return price[0]

def AddToSold(item, quant):

    current = GetSold(item)
    new = current[0] + int(quant)

    cursor = conn.cursor()
    cursor.execute("UPDATE laptops SET sold=" + str(new) + " WHERE item=" + f'"{item}"' )
    conn.commit()

def RemoveProduct(item):

    cursor = conn.cursor()
    cursor.execute("DELETE FROM laptops WHERE item=" + f'"{item}"')
    conn.commit()

## Endpoints ##
class Orders(Resource):
    def get(self):
        
        data = GetOrders()
        return data

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('item', required=True)  # add args
        parser.add_argument('item-quantity', required=True)
        parser.add_argument('memory', required=True)
        parser.add_argument('memory-quantity', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        get_item = GetStock(str(args['item']))
        get_memory = GetStock(str(args['memory']))


        if get_item[0] < int(args['item-quantity']):
            statement = str(args['item'] + " is out of stock.")
        elif get_memory[0] < int(args['memory-quantity']):
            statement = str(args['memory'] + " is out of stock.")
        else: 
            removeFromStock(str(args['item']), str(args['item-quantity']))
            removeFromStock(str(args['memory']), str(args['memory-quantity']))
            AddToSold(str(args['item']), str(args['item-quantity']))
            AddToSold(str(args['memory']), str(args['memory-quantity']))

            total = (c_laptop * int(args['item-quantity'])) + (GetPrice(str(args['memory'])) * int(args['memory-quantity']))

            statement = "Order placed! Total price: " + str(total)

        return statement


class Product(Resource):

    def get(self):

        data = GetAllProduct("""SELECT * FROM laptops""")
        return data

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('item', required=True)  # add args
        parser.add_argument('stock', required=True)
        parser.add_argument('sold', required=True)
        parser.add_argument('price', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        AddProduct(args['item'], str(args['stock']), str(args['sold']), str(args['price']))

        return GetAllProduct("""SELECT * FROM laptops""")

    def put(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('item', required=True)  # add args
        parser.add_argument('stock', required=True)
        parser.add_argument('price', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        UpdateProduct(args['item'], str(args['stock']), str(args['price']))

        return GetAllProduct("""SELECT * FROM laptops""")

    def delete(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('item', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary

        RemoveProduct(args['item'])

        return GetAllProduct("""SELECT * FROM laptops""")

api.add_resource(Orders, '/orders')
api.add_resource(Product, '/product')


if __name__ == '__main__':
    app.run(host='0.0.0.0')