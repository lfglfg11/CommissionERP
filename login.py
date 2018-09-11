import sys

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainter, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QStyleOption, QStyle, QLineEdit
from PyQt5 import Qt, QtGui
from PyQt5.uic import loadUi
import resources


class Widget(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        loadUi('login.ui', self)
        # self.ui = Ui_Form()
        # self.ui.setupUi(self)
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)  # 去掉标题栏
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)  # 密码输入
        self.loginPushButton.setCursor(QCursor(Qt.Qt.PointingHandCursor))  # 鼠标显示为手形
        self.exitPushButton.setCursor(QCursor(Qt.Qt.PointingHandCursor))
        self.exitPushButton.clicked.connect(exit)

        self.__bPressFlag = False
        self.__beginDrag: QPoint = QPoint(0, 0)

    # 重写paintEvent，否则不能使用QSS样式表定义外观
    def paintEvent(self, a0: QtGui.QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 反锯齿
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        self.__bPressFlag = True
        self.__beginDrag = a0.pos()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        self.__bPressFlag = False

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent):
        if self.__bPressFlag:
            rel: QPoint = QPoint(QCursor.pos().x() - self.__beginDrag.x(), QCursor.pos().y() - self.__beginDrag.y())
            self.move(rel)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = Widget()
    myShow.show()
    sys.exit(app.exec_())