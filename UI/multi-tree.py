from PyQt4 import uic, QtGui, QtCore
import sys
import types

class MainFrame(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        tree = {'Countries': {
                    "USA": ["CA", "NY", "TX"],

                    "India": ["KA", "TN", "AP"]}
        }

        self.tree = QtGui.QTreeView(self)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.tree)

        root_model = QtGui.QStandardItemModel()
        self.tree.setModel(root_model)
        self._populateTree(tree, root_model.invisibleRootItem())

    def _populateTree(self, children, parent):
        for child in sorted(children):
            child_item = QtGui.QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, types.DictType):
                self._populateTree(children[child], child_item)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = MainFrame()
    main.show()
    sys.exit(app.exec_())