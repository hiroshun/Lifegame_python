#!/usr/local/bin/python3

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIntValidator)
from PyQt5.QtWidgets import (QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton)

# セルの個数
CELL_HORIZONTAL = 50
CELL_VERTICAL = 50
# セルのサイズ
CELL_SIZE = 20
# オート実行時のスピード(ms)
AUTO_SPEED = 100
# 世代の最大値
MAX_GENE = 1000

class LifeGame(QGraphicsItem):
    def __init__(self, cell_horiz, cell_vert, size):
        super(LifeGame, self).__init__()
        self.cell_horiz = cell_horiz
        self.cell_vert = cell_vert
        self.size = size
        self.width = cell_horiz * size
        self.height = cell_vert * size
        self.gene = 0
        self.max_gene = MAX_GENE
        self.boards = []

        self.reset()

    def reset(self):
        self.boards = []
        # セル状態のリスト確保
        for g in range(self.max_gene):
            board = []
            # 上下1マスずつ余分に確保
            for y in range(self.cell_vert + 2):
                board.append([0] * (self.cell_horiz + 2))
            self.boards.append(board)

        self.gene = 0
        self.update()

    def paint(self, painter, option, widget):
        # セル境界線描画
        painter.setPen(QColor(220,220,220))
        for y in range(0,self.cell_vert+1):
            painter.drawLine(0, y*self.size, self.width, y*self.size)
        for x in range(0,self.cell_horiz+1):
            painter.drawLine(x*self.size, 0, x*self.size, self.height)

        # セル生存時、黒で塗りつぶす
        painter.setBrush(Qt.black)
        for y in range(self.cell_vert+1):
            for x in range(self.cell_horiz+1):
                if self.boards[self.gene][y+1][x+1] == 1:
                    painter.drawRect(self.size*x, self.size*y, self.size, self.size)

    def do_prev(self):
        if self.gene == 0:
            return
        self.gene -= 1
        self.update()
        return True

    def do_next(self):
        # 現在の世代が最大世代であれば更新しない
        if self.gene == self.max_gene - 1:
            return False

        change = False

        # 全セルの状態が前の世代と変わらなければ更新しない
        for y in range(self.cell_vert + 2):
            for x in range(self.cell_horiz + 2):
                if self.boards[self.gene-1][y][x] != self.boards[self.gene][y][x]:
                    change = True
                    break
            if change == True:
                break

        if change == False:
            return False

        # 次世代の計算
        for y in range(1, self.cell_vert+1):
            for x in range(1, self.cell_horiz+1):
                t = sum(self.boards[self.gene][y-1][x-1:x+2]) + \
                    self.boards[self.gene][y][x-1] + self.boards[self.gene][y][x+1] + \
                    sum(self.boards[self.gene][y+1][x-1:x+2])
                if self.boards[self.gene][y][x] == 0:
                    if t == 3:
                        self.boards[self.gene+1][y][x] = 1
                else:
                    if t == 2 or t == 3:
                        self.boards[self.gene+1][y][x] = 1

        self.gene += 1
        self.update()
        return True

    def boundingRect(self):
        return QRectF(0, 0, self.width,self.height)

    def mousePressEvent(self, event):
        if self.gene != 0:
            return
        pos = event.pos()
        self.select(int(pos.x()/self.size)+1, int(pos.y()/self.size)+1)
        self.update()
        super(LifeGame, self).mousePressEvent(event)

    def select(self, x, y):
        self.boards[self.gene][y][x] = 1 - self.boards[self.gene][y][x]

class MainWindow(QWidget):
    def __init__(self, horizontal, vertical, size, auto_speed, parent=None):
        super(MainWindow, self).__init__(parent)
        self.graphicsView = QGraphicsView()
        scene = QGraphicsScene(self.graphicsView)
        scene.setSceneRect(0, 0, horizontal*size, vertical*size)
        self.graphicsView.setScene(scene)
        self.lifegame = LifeGame(horizontal, vertical, size)
        scene.addItem(self.lifegame)
        self.auto_speed = auto_speed

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
        self.timer.setInterval(self.auto_speed)
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

    mainWindow = MainWindow(
        horizontal=CELL_HORIZONTAL, vertical=CELL_VERTICAL, size=CELL_SIZE, auto_speed=AUTO_SPEED
    )
    mainWindow.show()

    sys.exit(app.exec_())
