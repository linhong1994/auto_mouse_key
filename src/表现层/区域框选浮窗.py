from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QCursor, QMouseEvent, QPaintEvent


class 区域框选浮窗类(QWidget):
    """全屏区域框选浮窗，鼠标拖动选择矩形区域，实时可视化显示选区"""

    区域已选中 = Signal(int, int, int, int)  # 左上X, 左上Y, 右下X, 右下Y
    框选已取消 = Signal()  # 用户取消框选

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self._起始点 = None
        self._当前点 = None
        self._拖动中 = False

        self._字体 = QFont("Microsoft YaHei", 10)
        self._笔刷绿 = QColor(0, 255, 0)
        self._填充绿 = QColor(0, 255, 0, 40)
        self._背景色 = QColor(0, 0, 0, 100)
        self._提示色 = QColor(255, 255, 255, 200)

    def 启动框选(self) -> None:
        """启动全屏框选模式"""
        from PySide6.QtWidgets import QApplication
        屏幕 = QApplication.primaryScreen()
        if 屏幕:
            几何 = 屏幕.geometry()
            self.setGeometry(几何)
        else:
            self.showMaximized()
        self.show()
        self.activateWindow()
        self.raise_()

    def 关闭框选(self) -> None:
        """关闭框选浮窗"""
        self._起始点 = None
        self._当前点 = None
        self._拖动中 = False
        self.hide()

    # ── 鼠标事件 ──

    def mousePressEvent(self, 事件: QMouseEvent) -> None:
        if 事件.button() == Qt.MouseButton.LeftButton:
            self._起始点 = 事件.position().toPoint()
            self._当前点 = self._起始点
            self._拖动中 = True
            self.update()
        elif 事件.button() == Qt.MouseButton.RightButton:
            self.关闭框选()
            self.框选已取消.emit()

    def mouseMoveEvent(self, 事件: QMouseEvent) -> None:
        if self._拖动中:
            self._当前点 = 事件.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, 事件: QMouseEvent) -> None:
        if 事件.button() == Qt.MouseButton.LeftButton and self._拖动中 and self._起始点:
            终点 = 事件.position().toPoint()
            X1 = min(self._起始点.x(), 终点.x())
            Y1 = min(self._起始点.y(), 终点.y())
            X2 = max(self._起始点.x(), 终点.x())
            Y2 = max(self._起始点.y(), 终点.y())
            self._拖动中 = False
            self.关闭框选()
            if X2 - X1 > 5 and Y2 - Y1 > 5:
                self.区域已选中.emit(X1, Y1, X2, Y2)
            else:
                self.框选已取消.emit()

    def keyPressEvent(self, 事件) -> None:
        if 事件.key() == Qt.Key.Key_Escape:
            self.关闭框选()
            self.框选已取消.emit()

    # ── 绘制 ──

    def paintEvent(self, 事件: QPaintEvent) -> None:
        画笔 = QPainter(self)
        画笔.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 半透明遮罩背景
        画笔.fillRect(self.rect(), self._背景色)

        if self._拖动中 and self._起始点 and self._当前点:
            选区 = QRect(
                min(self._起始点.x(), self._当前点.x()),
                min(self._起始点.y(), self._当前点.y()),
                abs(self._当前点.x() - self._起始点.x()),
                abs(self._当前点.y() - self._起始点.y()),
            )

            # 选区内填充（高亮）
            画笔.fillRect(选区, self._填充绿)

            # 选区边框
            笔 = QPen(self._笔刷绿, 2, Qt.PenStyle.SolidLine)
            画笔.setPen(笔)
            画笔.drawRect(选区)

            # 坐标标签
            画笔.setFont(self._字体)
            画笔.setPen(self._笔刷绿)
            标签文本 = f"({选区.left()}, {选区.top()})"
            画笔.drawText(选区.left() + 4, 选区.top() - 6, 标签文本)

            标签文本2 = f"({选区.right()}, {选区.bottom()})"
            画笔.drawText(
                max(选区.right() - 140, 选区.left()),
                选区.bottom() + 16,
                标签文本2,
            )

            # 尺寸标签
            宽 = 选区.width()
            高 = 选区.height()
            尺寸文本 = f"{宽} × {高}"
            画笔.setPen(self._提示色)
            画笔.drawText(
                选区.center().x() - 30,
                选区.center().y(),
                尺寸文本,
            )
        else:
            # 未拖动时显示操作提示
            画笔.setFont(self._字体)
            画笔.setPen(self._提示色)
            提示 = "按住鼠标左键拖动选择区域    右键 / ESC 取消"
            画笔.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 提示)

        画笔.end()
