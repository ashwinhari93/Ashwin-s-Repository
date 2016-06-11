from pymongo import MongoClient
import os,csv,time,json

client = MongoClient()
db = client.pressure
listoffiles = ["test_car.json","test_car2.json","test_car3.json","test_car4.json","test_car5.json","test_car6.json","test_car7.json","test_car8.json","test_car9.json"]


with open('/home/ashwin/Documents/test_carlog.csv', 'w') as csvfile:
    fieldnames = ['File', 'Size(bytes)', 'Insertion time(seconds)', 'Average Insertion time(seconds)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i in listoffiles:
        sum = 0
        for k in xrange(10):
            ffile = open(i).read()
            raw_objs_string = ffile.replace('}\n{', '},{')
            arrayofobjects = '[%s]' % (raw_objs_string)
            objs = json.loads(arrayofobjects)
            size = os.path.getsize(i)
            start = time.clock()
            for j in objs:
                result = db.testdata.insert_one(j)
            end = time.clock()
            sum += (end-start)
            writer.writerow({'File': str(i), 'Size(bytes)': str(size), 'Insertion time(seconds)': str(end - start), 'Average Insertion time(seconds)': ' '})
        avg = sum/10;
        writer.writerow({'File': ' ', 'Size(bytes)': ' ', 'Insertion time(seconds)': ' ', 'Average Insertion time(seconds)': str(avg)})
        writer.writerow({'File': ' ', 'Size(bytes)': ' ', 'Insertion time(seconds)': ' ', 'Average Insertion time(seconds)': ' '})
csvfile.close()


