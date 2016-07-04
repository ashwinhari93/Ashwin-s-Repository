import sys, shutil, time, os, subprocess
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pymongo import MongoClient
from bson.objectid import ObjectId
from PyQt4.phonon import Phonon
import zipfile, re
from docx import Document



qtCreatorFile = "/home/ashwin/DR/input_module.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

fname = ''
type = ''
objectid = ''
ext = ''

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.browse.clicked.connect(self.file_browse)
        self.upload.clicked.connect(self.upload_file)
        self.tags.textChanged.connect(self.similarObjectDisplay)
        self.stop.clicked.connect(self.stop_video)
        self.start.clicked.connect(self.start_video)
        self.stop_2.clicked.connect(self.stop_video_2)
        self.start_2.clicked.connect(self.start_video_2)
        self.item_table.itemClicked.connect(self.tagClicked)
        self.table_scroll.setWidget(self.item_table)

    def similarObjectDisplay(self):
        tag_string = str(self.tags.toPlainText())
        tag_string_spaceless = tag_string.replace(' ','')
        tag_array = tag_string_spaceless.split(',')
        tag_set = set(tag_array)
        print tag_set
        client = MongoClient()
        db = client.dr_schemas
        files_in_db = db.file_schema.find()

        self.item_table.setRowCount(0)
        self.item_table.setColumnCount(3)
        self.item_table.setHorizontalHeaderLabels(['Type','Tags','Path'])
        for files in files_in_db:
            spaceless_tags = files['Tags'].replace(' ', '')
            phrase_set = set(spaceless_tags.split(','))

            if tag_set <= phrase_set:
                print "Type: " + files['Type'] + " Tags: " + files['Tags']
                rowPosition = self.item_table.rowCount()
                self.item_table.insertRow(rowPosition)
                self.item_table.setItem(rowPosition,0,QTableWidgetItem(files['Type']))
                self.item_table.setItem(rowPosition,1,QTableWidgetItem(files['Tags']))
                self.item_table.setItem(rowPosition,2,QTableWidgetItem(files['Path']))
        self.item_table.resizeColumnsToContents()


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
        global objectid, ext

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
                "Tags": str(tags),
                "Path": str(flat_file_path),
                "Linked Files": []
            })

            objectid = result.inserted_id

            flat_file_path_mongo = '/home/ashwin/FLAT_FILE_SYSTEM/%s' % (str(result.inserted_id) + "." + ext)

            shutil.copy2(fname, flat_file_path_mongo)

            db.file_schema.update_one({"Name": str(filename_part[len(filename_part) - 1])},
                                      {"$set": {"Path": str(flat_file_path_mongo)}})

            self.checkTags(str(tags))

            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)

            msg.setText("File uploaded")

            msg.setWindowTitle("Success")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()

    def checkTags(self, tags):
        global objectid
        t = tags.split(',')
        client = MongoClient()

        db = client.dr_schemas
        for i in t:
            tagcursor = db.tags_schema.find({"tag": str(i)}, {"_id": 0, "objectid": 1})
            if (tagcursor.count() != 0):
                for document in tagcursor:
                    db.tags_schema.update(
                        {"tag": str(i)},
                        {
                            "$set": {
                                #"filename": document['filename'] + ',' + str(global_filename)
                                "objectid" : document['objectid'] + ',' + str(objectid)
                            },
                            "$currentDate": {"lastModified": True}
                        }
                    )
            else:
                db.tags_schema.insert_one({
                    "tag": str(i),
                    "objectid": str(objectid)
                })


    def start_video(self):
        self.vp.play()

    def stop_video(self):
        self.vp.stop()

    def start_video_2(self):
        self.vp_2.play()

    def stop_video_2(self):
        self.vp_2.stop()


    def tagClicked(self, item):
        self.tabWidget_2.show()
        client = MongoClient()
        db = client.dr_schemas
        print item.text()
        cursor = db.file_schema.find({"Path": str(item.text())})

        for document in cursor:
            if document['Type'] == 'Image':
                self.stop_2.hide()
                self.start_2.hide()
                self.text_preview_2.setText("")
                self.tabWidget_2.setCurrentIndex(0)
                pixmap = QtGui.QPixmap(document['Path'])
                pixmap = pixmap.scaledToHeight(200)
                self.image_preview_2.setPixmap(pixmap)

            elif document['Type'] == 'Text':
                self.stop_2.hide()
                self.start_2.hide()
                self.image_preview_2.clear()
                self.scrollArea_2.setWidget(self.text_preview_2)
                self.tabWidget_2.setCurrentIndex(2)
                fileopen = open(document['Path']).read()
                self.text_preview_2.setText(fileopen)

            elif document['Type'] == 'Video':
                self.stop_2.show()
                self.start_2.show()
                #self.gridLayout_3.addWidget(self.vp, 0, 0, 2, 2)
                self.tabWidget_2.setCurrentIndex(1)
                self.vp_2.show()
                media = Phonon.MediaSource(document['Path'])
                self.vp_2.load(media)
                self.vp_2.play()

    def previewfile(self,path):
            global type
            if(type == 'Image'):

                self.stop.hide()
                self.start.hide()
                self.text_preview.setText("")
                self.tabWidget.setCurrentIndex(0)
                pixmap = QtGui.QPixmap(path)
                pixmap = pixmap.scaledToHeight(400)
                self.image_preview.setPixmap(pixmap)

            elif(type == 'Video'):
                self.stop.show()
                self.start.show()
                #self.gridLayout_3.addWidget(self.vp, 0, 0, 2, 2)
                self.tabWidget.setCurrentIndex(1)
                self.vp.show()
                media = Phonon.MediaSource(path)
                self.vp.load(media)
                self.vp.play()


            else:
                self.stop.hide()
                self.start.hide()
                self.image_preview.clear()
                self.scrollArea.setWidget(self.text_preview)
                self.tabWidget.setCurrentIndex(2)
                fileopen = open(path).read()
                self.text_preview.setText(fileopen)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())