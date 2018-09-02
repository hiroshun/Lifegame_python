#!/usr/local/bin/python3

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIntValidator)
from PyQt5.QtWidgets import (QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton)

SQUARE_WIDTH = 100
SQUARE_HEIGHT = 100
SQUARE_PIXEL = 20

class LifeGame(QGraphicsItem):
    def __init__(self, width=SQUARE_WIDTH, height=SQUARE_HEIGHT, size=SQUARE_PIXEL):
        super(LifeGame, self).__init__()
        self.width = width
        self.height = height
        self.max_gene = 1000
        self.gene = 0
        self.size = size
        self.NH = self.height//size 
        self.NW = self.width//size
        self.board = []

        for g in range(self.max_gene):
            board_tmp = []
            for y in range(self.NH + 2):
                board_tmp.append([0] * (self.NW + 2))
            self.board.append(board_tmp)

    def reset(self):
        self.board = []
        for g in range(self.max_gene):
            board_tmp = []
            for y in range(self.NH + 2):
                board_tmp.append([0] * (self.NW + 2))
            self.board.append(board_tmp)

        self.gene = 0
        self.update()

    def paint(self, painter, option, widget):
        painter.setPen(QColor(220,220,220))
        for y in range(0,self.NH+1):
            painter.drawLine(0, y*self.size, self.width, y*self.size)
        for x in range(0,self.NW+1):
            painter.drawLine(x*self.size, 0, x*self.size, self.height)

        painter.setBrush(Qt.black)
        for y in range(self.NH+1):
            for x in range(self.NW+1):
                if self.board[self.gene][y+1][x+1] == 1:
                    painter.drawRect(self.size*x, self.size*y, self.size, self.size)

    def do_prev(self):
        if self.gene == 0:
            return
        self.gene -= 1
        self.update()

    def do_next(self):
        if self.gene == self.max_gene - 1:
            return False
        flg = 0
        for y in range(self.NH + 2):
            for x in range(self.NW + 2):
                if self.board[self.gene-1][y][x] != \
                    self.board[self.gene][y][x]:
                    flg = 1
                    break
            if flg == 1:
                break
        if flg == 0:
            return False

        for y in range(1, self.NH+1):
            for x in range(1, self.NW+1):
                t = sum(self.board[self.gene][y-1][x-1:x+2]) + \
                    self.board[self.gene][y][x-1] + self.board[self.gene][y][x+1] + \
                    sum(self.board[self.gene][y+1][x-1:x+2])
                if self.board[self.gene][y][x] == 0:
                    if t == 3:
                        self.board[self.gene+1][y][x] = 1
                else:
                    if t == 2 or t == 3:
                        self.board[self.gene+1][y][x] = 1

        self.gene += 1
        self.update()
        return True

    def boundingRect(self):
        return QRectF(0,0,self.width,self.height)

    def mousePressEvent(self, event):
        if self.gene != 0:
            return
        pos = event.pos()
        self.select(int(pos.x()/self.size)+1, int(pos.y()/self.size)+1)
        self.update()
        super(LifeGame, self).mousePressEvent(event)

    def select(self, x, y):
        self.board[self.gene][y][x] = 1 - self.board[self.gene][y][x]

class MainWindow(QWidget):
    def __init__(self, parent=None):
        #set size
        width = 2000
        height = 2000
        size = 20
        super(MainWindow, self).__init__(parent)
        self.graphicsView = QGraphicsView()
        scene = QGraphicsScene(self.graphicsView)
        scene.setSceneRect(0, 0, width, height)
        self.graphicsView.setScene(scene)
        self.lifegame = LifeGame(width,height,size)
        scene.addItem(self.lifegame)

        self.genelabel = QLabel("GENE: " + str(self.lifegame.gene))
        self.resetButton = QPushButton("&Reset")
        self.resetButton.clicked.connect(self.reset)
        self.nextButton = QPushButton("&Next")
        self.nextButton.clicked.connect(self.do_next)
        self.prevButton = QPushButton("&Prev")
        self.prevButton.clicked.connect(self.do_prev)
        self.autoButton = QPushButton("&Auto")
        self.autoButton.clicked.connect(self.auto)
        self.stopButton = QPushButton("&Stop")
        self.stopButton.clicked.connect(self.stop)
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.genelabel)
        buttonLayout.addWidget(self.resetButton)
        buttonLayout.addWidget(self.nextButton)
        buttonLayout.addWidget(self.prevButton)
        buttonLayout.addWidget(self.autoButton)
        buttonLayout.addWidget(self.stopButton)

        propertyLayout = QVBoxLayout()
        propertyLayout.setAlignment(Qt.AlignTop)
        propertyLayout.addLayout(buttonLayout)

        mainLayout = QHBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(self.graphicsView)
        mainLayout.addLayout(propertyLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle("Life Game")
        self.timer = None

    def genelabel_update(self):
        self.genelabel.setText("GENE: " + str(self.lifegame.gene))

    def do_next(self):
        s = self.lifegame.do_next()
        self.genelabel_update()
        return s

    def do_prev(self):
        self.lifegame.do_prev()
        self.genelabel_update()

    def reset(self):
        self.lifegame.reset()
        self.genelabel_update()

    def auto(self):
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timeout)
        self.timer.start()

    def timeout(self):
        r = self.do_next()
        if not r:
            self.stop()

    def stop(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    sys.exit(app.exec_())
