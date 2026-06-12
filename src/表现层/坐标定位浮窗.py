from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPaintEvent


class 坐标定位浮窗类(QWidget):
    """屏幕坐标定位浮窗，在指定坐标位置叠加显示定位标识和步骤名称"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._定位类型 = "单点"
        self._坐标X = 0
        self._坐标Y = 0
        self._区域右下X = 0
        self._区域右下Y = 0
        self._步骤名称 = ""
        self._字体 = QFont("Microsoft YaHei", 12, QFont.Weight.Bold)
        self._十字大小 = 12
        self._文本边距 = 6
        self._自动关闭定时器 = QTimer(self)
        self._自动关闭定时器.setSingleShot(True)
        self._自动关闭定时器.timeout.connect(self.hide)

    def 显示单点定位(self, 坐标X: int, 坐标Y: int, 步骤名称: str, 显示时长: int = 3000) -> None:
        """在指定坐标点显示+步骤名称标识"""
        self._定位类型 = "单点"
        self._坐标X = 坐标X
        self._坐标Y = 坐标Y
        self._步骤名称 = 步骤名称
        self._计算窗口位置_单点()
        self.show()
        self.update()
        self._自动关闭定时器.start(显示时长)

    def 显示区域定位(self, 右下角X: int, 右下角Y: int, 步骤名称: str, 显示时长: int = 3000) -> None:
        """在区域右下角显示步骤名称标识"""
        self._定位类型 = "区域"
        self._区域右下X = 右下角X
        self._区域右下Y = 右下角Y
        self._步骤名称 = 步骤名称
        self._计算窗口位置_区域()
        self.show()
        self.update()
        self._自动关闭定时器.start(显示时长)

    def 关闭定位(self) -> None:
        """关闭定位浮窗"""
        self._自动关闭定时器.stop()
        self.hide()

    def _计算窗口位置_单点(self) -> None:
        """计算单点定位的窗口位置和大小，将物理坐标转为Qt逻辑坐标"""
        缩放比 = self._获取DPI缩放比()
        逻辑X = int(self._坐标X / 缩放比)
        逻辑Y = int(self._坐标Y / 缩放比)
        文本 = f"+{self._步骤名称}"
        文本宽度 = self._估算文本宽度(文本)
        文本高度 = 20
        十字半 = self._十字大小
        窗口宽度 = 十字半 * 2 + self._文本边距 + 文本宽度 + self._文本边距
        窗口高度 = max(十字半 * 2, 文本高度) + self._文本边距 * 2
        左上X = 逻辑X - 十字半
        左上Y = 逻辑Y - 十字半
        左上X, 左上Y = self._调整边界(左上X, 左上Y, 窗口宽度, 窗口高度)
        self.setGeometry(左上X, 左上Y, 窗口宽度, 窗口高度)

    def _计算窗口位置_区域(self) -> None:
        """计算区域定位的窗口位置和大小，将物理坐标转为Qt逻辑坐标"""
        缩放比 = self._获取DPI缩放比()
        逻辑X = int(self._区域右下X / 缩放比)
        逻辑Y = int(self._区域右下Y / 缩放比)
        文本宽度 = self._估算文本宽度(self._步骤名称)
        文本高度 = 20
        窗口宽度 = 文本宽度 + self._文本边距 * 2
        窗口高度 = 文本高度 + self._文本边距 * 2
        左上X = 逻辑X + 4
        左上Y = 逻辑Y - 窗口高度
        左上X, 左上Y = self._调整边界(左上X, 左上Y, 窗口宽度, 窗口高度)
        self.setGeometry(左上X, 左上Y, 窗口宽度, 窗口高度)

    def _调整边界(self, 左上X: int, 左上Y: int, 宽度: int, 高度: int) -> tuple[int, int]:
        """调整窗口位置确保不超出屏幕边界"""
        from PySide6.QtWidgets import QApplication
        屏幕 = QApplication.primaryScreen()
        if 屏幕:
            屏幕几何 = 屏幕.geometry()
            屏幕宽 = 屏幕几何.width()
            屏幕高 = 屏幕几何.height()
            if 左上X + 宽度 > 屏幕宽:
                左上X = 屏幕宽 - 宽度
            if 左上Y + 高度 > 屏幕高:
                左上Y = 屏幕高 - 高度
            if 左上X < 0:
                左上X = 0
            if 左上Y < 0:
                左上Y = 0
        return 左上X, 左上Y

    def _估算文本宽度(self, 文本: str) -> int:
        """估算文本像素宽度"""
        from PySide6.QtGui import QFontMetrics
        字体度量 = QFontMetrics(self._字体)
        return 字体度量.horizontalAdvance(文本)

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

    def paintEvent(self, 事件: QPaintEvent) -> None:
        """绘制定位标识"""
        画笔 = QPainter(self)
        画笔.setRenderHint(QPainter.RenderHint.Antialiasing)
        背景色 = QColor(0, 0, 0, 180)
        文字色 = QColor(255, 255, 255)
        十字色 = QColor(255, 80, 80)
        边框色 = QColor(255, 80, 80, 200)

        if self._定位类型 == "单点":
            self._绘制单点定位(画笔, 背景色, 文字色, 十字色, 边框色)
        else:
            self._绘制区域定位(画笔, 背景色, 文字色, 边框色)
        画笔.end()

    def _绘制单点定位(self, 画笔, 背景色, 文字色, 十字色, 边框色) -> None:
        """绘制单点坐标定位：+符号居中对齐坐标点，右侧显示步骤名称"""
        十字半 = self._十字大小
        中心X = 十字半
        中心Y = 十字半
        窗口高 = self.height()

        画笔.fillRect(self.rect(), 背景色)
        笔 = QPen(十字色, 2)
        画笔.setPen(笔)
        画笔.drawLine(中心X - 十字半, 中心Y, 中心X + 十字半, 中心Y)
        画笔.drawLine(中心X, 中心Y - 十字半, 中心X, 中心Y + 十字半)

        画笔.setFont(self._字体)
        画笔.setPen(文字色)
        文本 = f"+{self._步骤名称}"
        文本X = 十字半 + self._文本边距
        文本Y = (窗口高 + 画笔.fontMetrics().ascent() - 画笔.fontMetrics().descent()) // 2
        画笔.drawText(文本X, 文本Y, 文本)

        画笔.setPen(QPen(边框色, 1))
        画笔.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def _绘制区域定位(self, 画笔, 背景色, 文字色, 边框色) -> None:
        """绘制区域坐标定位：显示步骤名称"""
        画笔.fillRect(self.rect(), 背景色)
        画笔.setFont(self._字体)
        画笔.setPen(文字色)
        窗口高 = self.height()
        文本Y = (窗口高 + 画笔.fontMetrics().ascent() - 画笔.fontMetrics().descent()) // 2
        画笔.drawText(self._文本边距, 文本Y, self._步骤名称)

        画笔.setPen(QPen(边框色, 1))
        画笔.drawRect(self.rect().adjusted(0, 0, -1, -1))