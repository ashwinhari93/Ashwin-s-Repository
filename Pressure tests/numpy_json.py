try:
    import json
except ImportError:
    import simplejson as json
import numpy as np
import os
import time
from pymongo import MongoClient

client = MongoClient()
db = client.pressure_test

arr=np.arange(1500001)
dict_numpy = {}

for i in range(len(arr)):
    str_key = "num" + str(i)
    dict_numpy[str_key] = i

jsonarray = json.dumps(dict_numpy)
print jsonarray
file = open('pt1.json','w')
file.write(jsonarray)
file.close()
numpy_file = open('pt1.json','r').read()
filesize = os.path.getsize('pt1.json')
pt_data = json.loads(numpy_file)

start = time.clock()
db.pressure_test_col_1.insert_one(pt_data)
end = time.clock()
log_file = open('/home/ashwin/pressure_test_log.txt','a')
if(filesize<1024):
    print ("time to insert a file of size " + str(filesize) + " bytes into the db is " + str(end-start) + "seconds")
    log_str = "time to insert a file of size " + str(filesize) + " bytes into the db is " + str(end-start) + "seconds\n"
    log_file.write(log_str)
elif(filesize>1024 & filesize<(1024*1024)):
    print ("time to insert a file of size " + str(filesize/1024) + " KB into the db is " + str(end-start) + "seconds")
    log_str = "time to insert a file of size " + str(filesize/1024) + " KB into the db is " + str(end-start) + "seconds\n"
    log_file.write(log_str)
else:
    print ("time to insert a file of size " + str(filesize/(1024*1024)) + " MB into the db is " + str(end - start) + "seconds")