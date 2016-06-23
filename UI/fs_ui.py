import sys, shutil, time, os, subprocess
from PyQt4 import QtCore, QtGui, uic
from pymongo import MongoClient
qtCreatorFile = "/home/ashwin/DR/fs_ui.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

fname = ''
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

    def upload_file(self):
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

    def search_and_open(self):

        client = MongoClient()

        db = client.dr_schemas

        cursor = db.file_schema.find({"Name": str(self.search_box.toPlainText())},{"_id":0, "Path": 1})

        if(cursor.count()==0):

            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)

            msg.setText("Error. File not found")

            msg.setWindowTitle("Error")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()
        else:

            for document in cursor:



                print document['Path']

                subprocess.call(["xdg-open", document['Path']])




if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())