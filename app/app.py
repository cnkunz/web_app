from flask import Flask
from flask import jsonify
from flask_restful import Resource, Api, reqparse
import mysql.connector

app = Flask(__name__)
api = Api(app)

#########################
## MariaDB Connection ###
#########################
# This is the connection that all database functions will use
conn = mysql.connector.connect(user='root', password='dev', host='db', database='product') # DO NOT USE IN PRODUCTION

class create_dict(dict):

    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

#########################
### Database Functions ##
#########################
# Return every item in the database
def GetAllProduct(query):
    mydict = create_dict()
    select_stuff = query
    cursor = conn.cursor()
    cursor.execute(select_stuff)
    result = cursor.fetchall()

    for row in result:
        mydict.add(row[0],({"item":row[0],"stock":row[1],"sold":row[2],"price":row[3]}))

    stud_json = jsonify(mydict) # Jsonify might be unecessary

    return stud_json

# Returns available items, stock, and prices for users to see what they can buy
def GetAvailable():
    cursor = conn.cursor()
    cursor.execute("SELECT item, stock, price FROM laptops")
    result = cursor.fetchall()

    return result

# Get amount of sold for item in database, used for backend administrative information gathering
# Might be able to use this instead of GetSold()
# Try grabbing the second index? GetSold()[1]?
def GetOrders():
    cursor = conn.cursor()
    cursor.execute("SELECT item, sold FROM laptops")
    result = cursor.fetchall()

    return result

# Return amount of stock for item in database
# Used to ensure that there is enough of item in stock before allowing user to place order and decrement stock number
def GetStock(item):
#    mydict = create_dict()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM laptops WHERE item=" + f'"{item}"')
    result = cursor.fetchall()

    stock = [res[0] for res in result]

    return stock

# Used to increment sold number in database when order is placed
def GetSold(item):
    cursor = conn.cursor()
    cursor.execute("SELECT sold FROM laptops WHERE item=" + f'"{item}"')
    result = cursor.fetchall()

    sold = [res[0] for res in result]
    return sold

# Add's product item, stock, sold, and price to database
def AddProduct(item, stock, sold, price):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `laptops` (`item`, `stock`, `sold`, `price`) VALUES (" + f'"{item}"' + ", " + stock + ", " + sold + "," + price + ")")
    conn.commit()

# Update product's stock and price in database
# Does not update sold counter as we want this to be persistent
def UpdateProduct(item, stock, price):
    cursor = conn.cursor()
    cursor.execute("UPDATE laptops SET stock=" + stock + ", price=" + price + " WHERE item=" + f'"{item}"')
    conn.commit()

# Decrements stock counter when item is ordered by the amount tha tis ordered
def removeFromStock(item, quant):
#    cursor = conn.cursor()
    current = GetStock(item)
    new = current[0] - int(quant)

    cursor.execute("UPDATE laptops SET stock=" + str(new) + " WHERE item=" + f'"{item}"')
    conn.commit()

# Returns price field for item in database
# This returns in a list format, so we grab the first index as it will only return 1 object
# We grab the first index so that we can convert it to a string to concatenate it to the output statement
# (python can't concatenate strings and integers)
def GetPrice(memory):
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM laptops where item=" + f'"{memory}"')

    result = cursor.fetchall()
    price = [res[0] for res in result]

    return price[0]

# Increments sold counter for item in database
def AddToSold(item, quant):
    current = GetSold(item)
    new = current[0] + int(quant)

    cursor = conn.cursor()
    cursor.execute("UPDATE laptops SET sold=" + str(new) + " WHERE item=" + f'"{item}"' )
    conn.commit()

# Removes product entirely from database
def RemoveProduct(item):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM laptops WHERE item=" + f'"{item}"')
    conn.commit()

#########################
###### Endpoints ########
#########################
# /orders endpoint, this endpoint will be used for placing orders and getting the total price of the order
class Orders(Resource):
    # /orders get method to see everything in stock with prices
    def get(self):
        data = GetAvailable()
        return data
    
    # /orders post method to place an order, see total price, remove quantity from stock, and increment sold by quantity
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('item', required=True)
        parser.add_argument('item-quantity', required=True)
        parser.add_argument('memory', required=True)
        parser.add_argument('memory-quantity', required=True)
        args = parser.parse_args()

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

            total = (GetPrice(str(args['item'])) * int(args['item-quantity'])) + (GetPrice(str(args['memory'])) * int(args['memory-quantity']))

            statement = "Order placed! Total price: " + str(total)

        return statement

# /product endpoint, this endpoint will be used for looking at current stock, adding stock, removing stock, and updating existing stock
# Ideally this endpoint would be authentication controlled, allowing only authorised users access to the methods.
class Product(Resource):
    # /product get method to return everything in database to gather items, stock, sold, and prices
    def get(self):
        data = GetAllProduct("""SELECT * FROM laptops""")
        return data

    # /product post method to add products to database
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('item', required=True)
        parser.add_argument('stock', required=True)
        parser.add_argument('sold', required=True)
        parser.add_argument('price', required=True)
        args = parser.parse_args()

        AddProduct(args['item'], str(args['stock']), str(args['sold']), str(args['price']))

        return GetAllProduct("""SELECT * FROM laptops""")
    
    # /product put method to update existing products in database
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('item', required=True)
        parser.add_argument('stock', required=True)
        parser.add_argument('price', required=True)
        args = parser.parse_args()

        UpdateProduct(args['item'], str(args['stock']), str(args['price']))

        return GetAllProduct("""SELECT * FROM laptops""")
    
    # /product delete method to delete product from database
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('item', required=True)
        args = parser.parse_args()

        RemoveProduct(args['item'])

        return GetAllProduct("""SELECT * FROM laptops""")

# Generates endpoint resources
api.add_resource(Orders, '/orders')
api.add_resource(Product, '/product')

# Run with host=0.0.0.0 to make service externally available
if __name__ == '__main__':
    app.run(host='0.0.0.0')
