from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal
from src.公共.日志管理 import 获取日志管理器


class 系统托盘类(QSystemTrayIcon):
    """系统托盘图标与菜单"""

    显示主窗口信号 = Signal()
    启动录制信号 = Signal()
    启动回放信号 = Signal()
    退出信号 = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.日志 = 获取日志管理器("系统托盘")
        self.初始化托盘()

    def 初始化托盘(self) -> None:
        """初始化系统托盘"""
        self.setToolTip("自动操作工具")

        菜单 = QMenu()
        显示动作 = QAction("显示主窗口", self)
        显示动作.triggered.connect(self.显示主窗口信号.emit)
        菜单.addAction(显示动作)

        菜单.addSeparator()

        录制动作 = QAction("启动录制", self)
        录制动作.triggered.connect(self.启动录制信号.emit)
        菜单.addAction(录制动作)

        回放动作 = QAction("启动回放", self)
        回放动作.triggered.connect(self.启动回放信号.emit)
        菜单.addAction(回放动作)

        菜单.addSeparator()

        退出动作 = QAction("退出", self)
        退出动作.triggered.connect(self.退出信号.emit)
        菜单.addAction(退出动作)

        self.setContextMenu(菜单)
        self.activated.connect(self._处理激活)

    def _处理激活(self, 原因) -> None:
        """处理托盘图标激活事件"""
        if 原因 == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.显示主窗口信号.emit()

    def 更新状态图标(self, 状态文本: str) -> None:
        """更新托盘图标状态提示"""
        self.setToolTip(f"自动操作工具 - {状态文本}")