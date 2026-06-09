from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer, Signal
from src.公共.枚举定义 import 运行状态枚举
from src.公共.日志管理 import 获取日志管理器


class 状态信息组件类(QWidget):
    """状态信息区组件"""

    def __init__(self, 执行引擎=None, 热键管理器=None, parent=None):
        super().__init__(parent)
        self.执行引擎 = 执行引擎
        self.热键管理器 = 热键管理器
        self.日志 = 获取日志管理器("状态信息组件")
        self.初始化界面()
        self.启动坐标更新()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QHBoxLayout(self)

        self.坐标标签 = QLabel("坐标: X=0, Y=0")
        布局.addWidget(self.坐标标签)

        self.状态标签 = QLabel("状态: 空闲")
        布局.addWidget(self.状态标签)

        self.热键标签 = QLabel("热键: F9录制 F10回放 Esc停止")
        布局.addWidget(self.热键标签)

    def 启动坐标更新(self) -> None:
        """启动鼠标坐标定时更新"""
        self.坐标定时器 = QTimer(self)
        self.坐标定时器.timeout.connect(self._更新坐标)
        self.坐标定时器.start(200)

    def _更新坐标(self) -> None:
        """更新鼠标坐标显示"""
        try:
            import pyautogui
            X, Y = pyautogui.position()
            self.坐标标签.setText(f"坐标: X={X}, Y={Y}")
        except Exception:
            pass

    def 更新执行状态(self, 状态: str, 进度: str) -> None:
        """更新执行状态显示"""
        self.状态标签.setText(f"状态: {状态} {进度}")

    def 更新热键显示(self, 热键配置: dict[str, str]) -> None:
        """更新热键配置显示"""
        录制键 = 热键配置.get("启动录制", "F9")
        回放键 = 热键配置.get("启动回放", "F10")
        停止键 = 热键配置.get("紧急停止", "Esc")
        self.热键标签.setText(f"热键: {录制键}录制 {回放键}回放 {停止键}停止")