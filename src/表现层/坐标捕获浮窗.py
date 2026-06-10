from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMouseEvent


class 坐标捕获浮窗类(QWidget):
    """坐标捕获浮窗，置顶显示实时鼠标坐标，支持自由拖拽"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(180, 32)
        self._拖拽偏移 = None
        self._初始化界面()
        self._坐标更新定时器 = QTimer(self)
        self._坐标更新定时器.timeout.connect(self._更新坐标显示)
        self._坐标更新定时器.setInterval(50)

    def _初始化界面(self) -> None:
        """初始化界面"""
        布局 = QHBoxLayout(self)
        布局.setContentsMargins(8, 4, 8, 4)
        self.坐标标签 = QLabel("坐标: 0, 0")
        self.坐标标签.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); color: #00ff00; "
            "font-size: 13px; padding: 2px 6px; border-radius: 4px;"
        )
        布局.addWidget(self.坐标标签)

    def 启动捕获(self) -> None:
        """启动坐标实时显示"""
        self._坐标更新定时器.start()
        self.show()

    def 停止捕获(self) -> None:
        """停止坐标实时显示"""
        self._坐标更新定时器.stop()
        self.hide()

    def _更新坐标显示(self) -> None:
        """定时更新鼠标坐标显示"""
        try:
            import pyautogui
            X, Y = pyautogui.position()
            self.坐标标签.setText(f"坐标: {X}, {Y}")
        except Exception:
            pass

    def 设置坐标(self, X: int, Y: int) -> None:
        """设置坐标值"""
        self.坐标标签.setText(f"坐标: {X}, {Y}")

    def mousePressEvent(self, 事件: QMouseEvent) -> None:
        """鼠标按下，开始拖拽"""
        if 事件.button() == Qt.MouseButton.LeftButton:
            self._拖拽偏移 = 事件.position().toPoint()

    def mouseMoveEvent(self, 事件: QMouseEvent) -> None:
        """鼠标移动，拖拽窗口"""
        if self._拖拽偏移 is not None:
            self.move(事件.globalPosition().toPoint() - self._拖拽偏移)

    def mouseReleaseEvent(self, 事件: QMouseEvent) -> None:
        """鼠标释放，结束拖拽"""
        self._拖拽偏移 = None