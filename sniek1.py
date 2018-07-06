import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# To show Qt framework messages.
QtCore.qInstallMessageHandler(lambda t, c, m: print(m))


T_BLOCK, T_EMPTY, T_SNAKE = 0, 1, 2

class Sniek(QtWidgets.QWidget):
    """
    M: map
    n, m: numbers of rows and columns of map
    S: position of each piece of snake (from head to tail)
    """
    
    def __init__(self):
        super().__init__()
        
        # Load map.
        with open('1.map') as f:
            f.readline()  # Skip setting.
            self.M = [[T_EMPTY if x == ' ' else T_BLOCK for x in list(l)]
                      for l in f.read().split('\n')]
        self.n, self.m = len(self.M) + 2, max(len(Mi) for Mi in self.M) + 2
        for Mi in self.M:
            Mi.insert(0, T_BLOCK)
            Mi.extend([T_EMPTY] * (self.m - len(Mi) - 1) + [T_BLOCK])
        self.M.insert(0, [T_BLOCK] * self.m)
        self.M.append([T_BLOCK] * self.m)
    
        # Initialize snake.
        self.S = [(i, self.m // 2) for i in range(self.n - 7, self.n - 1)]
        for i, j in self.S:
            self.M[i][j] = T_SNAKE
    
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        
        sz = self.size(); win_w, win_h = sz.width(), sz.height()
        
        # Fill background.
        painter.fillRect(0, 0, win_w, win_h, Qt.white)
        
        # Draw tiles.
        ts = min(win_w / self.m, win_h / self.n)  # tile size
        painter.translate((win_w - ts * self.m) / 2, (win_h - ts * self.n) / 2)
        painter.scale(ts, ts)
        for i in range(self.n):
            for j in range(self.m):
                if self.M[i][j] == T_BLOCK:
                    painter.fillRect(j, i, 1, 1, Qt.darkGray)
                elif self.M[i][j] == T_SNAKE:
                    painter.fillRect(j, i, 1, 1, Qt.green if (i, j) == self.S[0] else Qt.blue)
        
        painter.end()


app = QtWidgets.QApplication(sys.argv)

s = Sniek()
s.setWindowTitle('Sniek')
s.show()

sys.exit(app.exec_())
