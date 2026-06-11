from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from src.公共.日志管理 import 获取日志管理器


class 状态信息组件类(QWidget):
    """状态信息区组件"""

    def __init__(self, 执行引擎=None, 热键管理器=None, parent=None):
        super().__init__(parent)
        self.执行引擎 = 执行引擎
        self.热键管理器 = 热键管理器
        self.日志 = 获取日志管理器("状态信息组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QHBoxLayout(self)

        self.状态标签 = QLabel("状态: 空闲")
        布局.addWidget(self.状态标签)

    def 更新执行状态(self, 状态: str, 进度: str) -> None:
        """更新执行状态显示"""
        self.状态标签.setText(f"状态: {状态} {进度}")