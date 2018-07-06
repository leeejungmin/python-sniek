import sys, os
from random import randrange

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtCore import Qt, QRectF

# To show Qt framework messages.
QtCore.qInstallMessageHandler(lambda t, c, m: print(m))


T_BLOCK, T_EMPTY, T_SNAKE, T_FRUIT = 0, 1, 2, 3
S_READY, S_NEXT, S_STARTED, S_DIE, S_COMPLETE = 0, 1, 2, 3, 4
KD = {Qt.Key_Up: (-1, 0), Qt.Key_Down: (1, 0), Qt.Key_Left: (0, -1), Qt.Key_Right: (0, 1)}
KK = {Qt.Key_Up:   {Qt.Key_Left, Qt.Key_Right}, Qt.Key_Down:  {Qt.Key_Left, Qt.Key_Right},
      Qt.Key_Left: {Qt.Key_Up, Qt.Key_Down},    Qt.Key_Right: {Qt.Key_Up, Qt.Key_Down}}
S_TEXT = {S_READY: 'READY!', S_NEXT: 'NEXT LEVEL', S_STARTED: '',
          S_DIE: 'YOU DIED!', S_COMPLETE: 'COMPLETED!'}
    

class Sniek(QtWidgets.QWidget):
    """
    state: ready or started or terminated
    M: map
    n, m: numbers of rows and columns of map
    S: position of each piece of snake (from head to tail)
    d, d1, d2: current, next, and next^2 directions of head
    extend: how many more to extend
    """
    
    def __init__(self):
        super().__init__()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        
        self.sound1, self.sound2 = QtMultimedia.QSoundEffect(), QtMultimedia.QSoundEffect()
        self.sound1.setSource(QtCore.QUrl.fromLocalFile('tick.wav'))
        self.sound2.setSource(QtCore.QUrl.fromLocalFile('tick_f.wav'))
        
        self.bgm = QtMultimedia.QMediaPlayer()
        self.bgm.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile('bgm.mp3')))
        self.bgm.setVolume(70)
        self.bgm.play()
        
        self.level, self.goal = 1, 0
        self.get_ready()
    
    def get_ready(self):
        # Load map.
        with open('%d.map' % self.level) as f:
            self.goal, self.intv0, self.intv1, self.intv_d, self.add, self.n_fruit = eval(f.readline())
            self.M = [[T_EMPTY if x == ' ' else T_BLOCK for x in list(l)]
                      for l in f.read().split('\n')]
        self.n, self.m = len(self.M) + 2, max(len(Mi) for Mi in self.M) + 2
        for Mi in self.M:
            Mi.insert(0, T_BLOCK)
            Mi.extend([T_EMPTY] * (self.m - len(Mi) - 1) + [T_BLOCK])
        self.M.insert(0, [T_BLOCK] * self.m)
        self.M.append([T_BLOCK] * self.m)
        
        # Initialize snake.
        self.S = [(self.n - 2, self.m // 2)]
        self.M[self.S[0][0]][self.S[0][1]] = T_SNAKE
        
        # Etc.
        self.state, self.d, self.d1, self.d2 = S_READY, Qt.Key_Up, None, None
        self.score, self.extend = 0, self.add
    
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
                elif self.M[i][j] == T_FRUIT:
                    painter.fillRect(j, i, 1, 1, Qt.red)
        
        # Draw score and notice.
        painter.resetTransform()
        painter.setFont(QtGui.QFont('Arial', ts * 3))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 128, 128, 200)))
        painter.drawText(ts * 2, ts * 4, 'L%d %d/%d' % (self.level, self.score, self.goal))
        painter.setFont(QtGui.QFont('Arial', ts * 5))
        painter.drawText(QRectF(0, 0, win_w, win_h), Qt.AlignCenter, S_TEXT[self.state])
        
        painter.end()
    
    def keyPressEvent(self, e):
        if self.state == S_STARTED:
            if self.d1 is None:
                if e.key() in KK[self.d]:
                    self.d1 = e.key()
            elif self.d2 is None:
                if e.key() in KK[self.d1]:
                    self.d2 = e.key()
        
        elif e.key() == Qt.Key_Space:
            if self.state == S_READY:
                self.lay_fruit()
                self.timer.start(self.intv0)
                self.bgm.setVolume(40)
                self.bgm.setPosition(0)
                self.state = S_STARTED
            
            elif self.state == S_NEXT:
                self.level += 1
                self.get_ready()
                self.state = S_READY
            
            elif self.state == S_DIE or self.state == S_COMPLETE:
                self.level = 1
                self.get_ready()
            
            self.update()
    
    def lay_fruit(self):
        if (self.score % self.n_fruit) == 0:
            f = 0
            while f < self.n_fruit:
                i, j = randrange(self.n), randrange(self.m)
                if self.M[i][j] == T_EMPTY:
                    self.M[i][j] = T_FRUIT
                    f += 1
    
    def tick(self):
        # Handle key press.
        if self.d1:
            self.d, self.d1, self.d2 = self.d1, self.d2, None
        
        # Get next position of head.
        i, j = self.S[0][0] + KD[self.d][0], self.S[0][1] + KD[self.d][1]
        
        # Check next tile.
        if i >= 0 and (self.M[i][j] == T_BLOCK or self.M[i][j] == T_SNAKE):
            self.bgm.setVolume(60)
            self.bgm.setPosition(0)
            self.timer.stop()
            self.state = S_DIE
        
        else:
            # Check fruit.
            if self.M[i][j] == T_FRUIT:
                self.score += 1
                self.extend += self.add
                if self.score < self.goal:
                    self.lay_fruit()
                else:
                    self.M[0][self.m // 2] = T_EMPTY
                self.timer.setInterval(max(self.intv1, self.timer.interval() * self.intv_d))
            
            # Erase last piece.
            if self.extend > 0:
                self.sound2.play()
                self.extend -= 1
            else:
                self.sound1.play()
                i1, j1 = self.S.pop()
                self.M[i1][j1] = T_EMPTY
            
            # Add first piece or check completed.
            if i >= 0:
                # Add first piece
                self.S.insert(0, (i, j))
                self.M[i][j] = T_SNAKE
            else:
                if self.S:
                    self.timer.setInterval(10)
                else:
                    self.timer.stop()
                    if os.path.isfile('%s.map' % (self.level + 1)):
                        self.state = S_NEXT
                    else:
                        self.state = S_COMPLETE
        
        self.repaint()


app = QtWidgets.QApplication(sys.argv)

s = Sniek()
s.setWindowTitle('Sniek')
s.show()

sys.exit(app.exec_())
