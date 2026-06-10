from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QColor


class 遮罩层类(QWidget):
    """全屏透明遮罩层，拦截鼠标事件防止穿透到底层界面"""

    坐标捕获信号 = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._捕获模式 = False

    def 启动遮罩(self) -> None:
        """显示全屏遮罩并进入捕获模式"""
        self._捕获模式 = True
        屏幕 = self.screen().geometry()
        self.setGeometry(屏幕)
        self.show()

    def 停止遮罩(self) -> None:
        """隐藏遮罩并退出捕获模式"""
        self._捕获模式 = False
        self.hide()

    def mousePressEvent(self, 事件: QMouseEvent) -> None:
        """鼠标点击时捕获坐标"""
        if self._捕获模式 and 事件.button() == Qt.MouseButton.LeftButton:
            全局坐标 = 事件.globalPosition().toPoint()
            self.坐标捕获信号.emit(全局坐标.x(), 全局坐标.y())
            self.停止遮罩()
        elif self._捕获模式 and 事件.button() == Qt.MouseButton.RightButton:
            self.停止遮罩()

    def paintEvent(self, 事件) -> None:
        """绘制半透明遮罩"""
        画笔 = QPainter(self)
        画笔.fillRect(self.rect(), QColor(0, 0, 0, 30))