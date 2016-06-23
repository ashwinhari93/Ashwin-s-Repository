import json
from pymongo import MongoClient

list_of_schemas = ['File_schema.json','Opening_App.json','User_schema.json','Address_schema.json']
client = MongoClient()
db = client.dr_schemas

for i in list_of_schemas:
    fdesc = open('/home/ashwin/DR/Schemas/%s'%(i)).read()
    array_of_objs = '[%s]'%fdesc
    json_objs = json.loads(array_of_objs)

    if i=="File_schema.json":
        for j in json_objs:
            result = db.file_schema.insert_one(j)
    elif i == "Opening_App.json":
        for j in json_objs:
            result = db.appopen_schema.insert_one(j)
    elif i == "User_schema.json":
        for j in json_objs:
            result = db.user_schema.insert_one(j)
    elif i == "Address_schema.json":
        for j in json_objs:
            result = db.appopen_schema.insert_one(j)
