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
        """鼠标点击时捕获坐标，将Qt逻辑坐标转为物理坐标"""
        if self._捕获模式 and 事件.button() == Qt.MouseButton.LeftButton:
            逻辑坐标 = 事件.globalPosition().toPoint()
            缩放比 = self._获取DPI缩放比()
            物理X = int(逻辑坐标.x() * 缩放比)
            物理Y = int(逻辑坐标.y() * 缩放比)
            self.坐标捕获信号.emit(物理X, 物理Y)
            self.停止遮罩()
        elif self._捕获模式 and 事件.button() == Qt.MouseButton.RightButton:
            self.停止遮罩()

    def _获取DPI缩放比(self) -> float:
        """获取系统DPI缩放比例"""
        try:
            import ctypes
            桌面DC = ctypes.windll.user32.GetDC(0)
            水平DPI = ctypes.windll.gdi32.GetDeviceCaps(桌面DC, 88)
            ctypes.windll.user32.ReleaseDC(0, 桌面DC)
            return 水平DPI / 96.0
        except Exception:
            return 1.0

    def paintEvent(self, 事件) -> None:
        """绘制半透明遮罩"""
        画笔 = QPainter(self)
        画笔.fillRect(self.rect(), QColor(0, 0, 0, 30))