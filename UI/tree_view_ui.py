from PyQt4 import uic, QtGui, QtCore


(Ui_MainWindow, QMainWindow) = uic.loadUiType('/home/ashwin/DR/qt_treeview.ui')


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = QtGui.QStandardItemModel()
        self.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'), self.add_item)
        self.ui.treeView.setModel(self.model)

    def add_item(self):
        t = self.ui.lineEdit.text()
        if len(t) > 0:
            item = QtGui.QStandardItem(t)
            self.model.appendRow(item)
            self.ui.lineEdit.clear()
        else:
            self.ui.statusBar.showMessage('error: no text')


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())