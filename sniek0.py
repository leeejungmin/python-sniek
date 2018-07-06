import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# To show Qt framework messages.
QtCore.qInstallMessageHandler(lambda t, c, m: print(m))


class Sniek(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
    
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        
        painter.fillRect(100, 100, 150, 150, Qt.red)
        painter.drawRect(150, 150, 150, 150)
        
        painter.end()


app = QtWidgets.QApplication(sys.argv)

s = Sniek()
s.setWindowTitle('Sniek')
s.show()

sys.exit(app.exec_())
