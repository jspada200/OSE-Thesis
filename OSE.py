import sys
from OSE_Modules import MainWindow as mw
from PyQt4 import QtGui


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main_window = mw.MainWindow()
    main_window.show()

    sys.exit(app.exec_())