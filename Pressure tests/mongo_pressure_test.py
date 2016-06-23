import json
import re
import os
import time

from pymongo import MongoClient
client = MongoClient()
db = client.pressure_test
#list_of_files = ['test_car.json','test_car2.json','test_car3.json','test_car4.json','test_car5.json','test_car6.json','test_car7.json','test_car8.json','test_car9.json']
#for files in list_of_files:
for i in range(0,10):
    raw_objs_string = open('test_car10.json').read() #read in raw data
    filesize = os.path.getsize('test_car10.json')

    objs_string = '[%s]'%(raw_objs_string) #wrap in a list, to make valid json
    objs = json.loads(objs_string)


    start = time.clock()
    for i in range(len(objs)):
        record = dict(objs[i])
        result = db.pressure_test_col_new_5.insert_one(record)
    end = time.clock()
    log_file = open('/home/ashwin/Documents/pt_log.txt','a')
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
    log_file.close()

