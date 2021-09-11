import mysql.connector
import json

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

mydict = create_dict()
select_stuff = """SELECT * FROM laptops"""
cursor = conn.cursor()
cursor.execute(select_stuff)
result = cursor.fetchall()

for row in result:
    mydict.add(row[0],({"item":row[0],"stock":row[1],"sold":row[2]}))

stud_json = json.dumps(mydict, indent=2, sort_keys=True)

print(stud_json)