import sys, shutil, time, os, subprocess
from PyQt4 import QtCore, QtGui, uic
from pymongo import MongoClient
qtCreatorFile = "/home/ashwin/DR/fs_ui.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

fname = ''
global_filename = ''

filelist = ''



class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.browse.clicked.connect(self.file_browse)
        self.upload.clicked.connect(self.upload_file)
        self.search_open.clicked.connect(self.search_and_open)

    def file_browse(self):
        global fname
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Browse file',
                                            '/home/ashwin')
        self.file_path.setText(fname)

    def file_exist_check(self, filename):
        client = MongoClient()
        db = client.dr_schemas
        cursor = db.file_schema.find({"Name": filename})
        print cursor.count()
        if (cursor.count() > 0):
            return 1;
        else:
            return 0;

    def upload_file(self):

        global global_filename
        if(self.file_path.toPlainText()==''):
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)

            msg.setText("Error. Please select a file")

            msg.setWindowTitle("Error")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()

        else:
            filename_part = fname.split('/')

            flat_file_path = '/home/ashwin/FLAT_FILE_SYSTEM/%s'%(filename_part[len(filename_part)-1])

            global_filename = str(filename_part[len(filename_part)-1])

            extension = filename_part[len(filename_part)-1].split('.')

            ext = extension[len(extension)-1]

            creation_time = time.ctime(os.path.getctime(fname))

            modified_time = time.ctime(os.path.getmtime(fname))


            file_size = os.path.getsize(fname)

            tags = self.tags.toPlainText()

            type = self.type.toPlainText()

            description = self.description.toPlainText()

            client = MongoClient()



            db = client.dr_schemas

            res_exist = self.file_exist_check(global_filename)

            print res_exist

            if(res_exist==1):
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Critical)

                msg.setText("Error. File exists")

                msg.setWindowTitle("Error")
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                msg.exec_()

            else:


                result = db.file_schema.insert_one({

      "Name":str(filename_part[len(filename_part)-1]),
      "Description": str(description) ,
      "Type":str(type),
      "Color": "",
      "Extension_Type":str(ext),
      "Creator Details":{
            "user id": "",
            "user name": "",
            "date of creation":str(creation_time),
            "group_id":""
      },

      "Size": str(file_size),
      "Modified":{
            "Number of Modifications": "",
            "Last Modified": str(modified_time)


      },
      "Log":[
          {
             "User Id": "",
             "User Name": "",
             "Date of Modification":"",
             "Details": ""
          }
      ],
      "Tags":[] ,
      "Path": str(flat_file_path),
      "Linked Files": []
    })

            print result.inserted_id

            flat_file_path_mongo = '/home/ashwin/FLAT_FILE_SYSTEM/%s'%(str(result.inserted_id)+"."+ext)

            shutil.copy2(fname, flat_file_path_mongo)

            db.file_schema.update_one({"Name":str(filename_part[len(filename_part)-1])},{"$set" : {"Path":str(flat_file_path_mongo)} })

            self.checkTags(str(tags))

    def checkTags(self, tags):
        t = tags.split(',')
        client = MongoClient()

        db = client.dr_schemas
        for i in t:
            tagcursor = db.tags_schema.find({"tag": str(i)}, {"_id": 0, "filename": 1})
            if (tagcursor.count() != 0):
                for document in tagcursor:
                    db.tags_schema.update(
                        {"tag": str(i)},
                        {
                            "$set": {
                                "filename": document['filename'] + ',' + str(global_filename)
                            },
                            "$currentDate": {"lastModified": True}
                        }
                    )
            else:
                db.tags_schema.insert_one({
                    "tag": str(i),
                    "filename": str(global_filename)
                })

    def search_and_open(self):
        global filelist

        if str(self.search_box.toPlainText()) != "":
            client = MongoClient()
            db = client.dr_schemas

            radiotag = self.radioTag.isChecked()
            radiofile = self.radioFile.isChecked()

            if radiotag == True:
                cursorcount = db.tags_schema.find({"tag": str(self.search_box.toPlainText())}, {"_id": 0, "filename": 1})
                if cursorcount.count() != 0:
                    for document in cursorcount:
                        filearry = document['filename'].split(',')

                        for j in filearry:
                            filelist += j + ","
                        print filelist
                        #self.results.setText(filelist)
                        # cursor = db.file.find({"Name": document['filename']}, {"_id": 0, "Path": 1})
                else:
                    msg = QtGui.QMessageBox()
                    msg.setIcon(QtGui.QMessageBox.Critical)

                    msg.setText("Error. File not found")

                    msg.setWindowTitle("Error")
                    msg.setStandardButtons(QtGui.QMessageBox.Ok)
                    msg.exec_()

            elif radiofile == True:
                cursor = db.file_schema.find({"Name": str(self.search_box.toPlainText())}, {"_id": 0, "Path": 1})

                if (cursor.count() == 0):

                    msg = QtGui.QMessageBox()
                    msg.setIcon(QtGui.QMessageBox.Critical)
                    msg.setText("Error. File not found")
                    msg.setWindowTitle("Error")
                    msg.setStandardButtons(QtGui.QMessageBox.Ok)
                    msg.exec_()
                else:

                    for document in cursor:
                        subprocess.call(["xdg-open", document['Path']])
                        #self.results.setText(str(self.Search.text()))
            else:
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Critical)
                msg.setText("Please Select File or Tag!!!")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                msg.exec_()
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setText("Please Enter File or Tag Name!!!")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())