import sys, shutil, time, os, subprocess
from PyQt4 import QtCore, QtGui, uic
from pymongo import MongoClient
qtCreatorFile = "/home/ashwin/DR/input_module.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

fname = ''
type = ''

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.browse.clicked.connect(self.file_browse)
        self.upload.clicked.connect(self.upload_file)

    def file_browse(self):
        global fname
        global type
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Browse file',
                                                  '/home/ashwin')
        self.file_path.setText(fname)

        filename_info = fname.split('/')

        self.name_disp.setText("Name: " + filename_info[len(filename_info)-1])

        self.date_disp.setText("Date: " + str(time.ctime(os.path.getctime(fname))))

        self.filesize_disp.setText("Filesize: " + str(os.path.getsize(fname)))

        extension = filename_info[len(filename_info) - 1].split('.')

        ext = extension[len(extension) - 1]

        self.format_disp.setText("Format: " + ext)



        if(ext=="jpg" or ext=="jpeg" or ext=="png" or ext=="gif" or ext=="bmp" or ext=="tiff"):
            self.type_disp.setText("Type: Image")
            type = 'Image'

        elif(ext=="avi" or ext=="mp4" or ext=="flv" or ext=="mov" or ext=="webm"):
            self.type_disp.setText("Type: Video")
            type = 'Video'

        elif(ext=="mp3" or ext=="m4a" or ext=="ogg"):
            self.type_disp.setText("Type: Audio")
            type = 'Audio'

        else:
            self.type_disp.setText("Type: Text")
            type = 'Text'

        self.previewfile(fname)

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
        global type
        if (self.file_path.toPlainText() == ''):
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)

            msg.setText("Error. Please select a file")

            msg.setWindowTitle("Error")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()
        else:
            filename_part = fname.split('/')

            flat_file_path = '/home/ashwin/FLAT_FILE_SYSTEM/%s' % (filename_part[len(filename_part) - 1])

            global_filename = str(filename_part[len(filename_part) - 1])

            extension = filename_part[len(filename_part) - 1].split('.')

            ext = extension[len(extension) - 1]

            creation_time = time.ctime(os.path.getctime(fname))

            modified_time = time.ctime(os.path.getmtime(fname))

            file_size = os.path.getsize(fname)

            tags = self.tags.toPlainText()



            description = self.description.toPlainText()

            project = self.project.toPlainText()

            date = self.date.toPlainText()

            client = MongoClient()

            db = client.dr_schemas

            res_exist = self.file_exist_check(global_filename)

            print res_exist

            if (res_exist == 1):
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Critical)

                msg.setText("Error. File exists")

                msg.setWindowTitle("Error")
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                msg.exec_()

            else:

                file_date = ''

                if(date==''):
                    file_date = str(creation_time)

                else:
                    file_date = str(date)

                result = db.file_schema.insert_one({

                    "Name": str(filename_part[len(filename_part) - 1]),
                    "Description": str(description),
                    "Type": type,
                    "Color": "",
                    "Project": str(project),
                    "Extension_Type": str(ext),
                    "Creator Details": {
                        "user id": "",
                        "user name": "",
                        "date of creation": file_date,
                        "group_id": ""
                    },

                    "Size": str(file_size),
                    "Modified": {
                        "Number of Modifications": "",
                        "Last Modified": str(modified_time)

                    },
                    "Log": [
                        {
                            "User Id": "",
                            "User Name": "",
                            "Date of Modification": "",
                            "Details": ""
                        }
                    ],
                    "Tags": [],
                    "Path": str(flat_file_path),
                    "Linked Files": []
                })

            print result.inserted_id

            flat_file_path_mongo = '/home/ashwin/FLAT_FILE_SYSTEM/%s' % (str(result.inserted_id) + "." + ext)

            shutil.copy2(fname, flat_file_path_mongo)

            db.file_schema.update_one({"Name": str(filename_part[len(filename_part) - 1])},
                                      {"$set": {"Path": str(flat_file_path_mongo)}})

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

    def previewfile(self,path):

            pixmap = QtGui.QPixmap(path)
            pixmap = pixmap.scaledToHeight(400)
            self.pre_input_preview.setPixmap(pixmap)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())