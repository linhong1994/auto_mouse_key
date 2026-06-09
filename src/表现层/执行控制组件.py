from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox, QSpinBox, QLabel
from PySide6.QtCore import Signal
from src.公共.日志管理 import 获取日志管理器


class 执行控制组件类(QWidget):
    """执行控制区组件"""

    回放信号 = Signal(float, int)
    停止信号 = Signal()
    录制信号 = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.日志 = 获取日志管理器("执行控制组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QHBoxLayout(self)

        self.回放按钮 = QPushButton("回放")
        self.回放按钮.clicked.connect(self._处理回放)
        布局.addWidget(self.回放按钮)

        self.停止按钮 = QPushButton("停止")
        self.停止按钮.clicked.connect(self.停止信号.emit)
        布局.addWidget(self.停止按钮)

        self.录制按钮 = QPushButton("录制")
        self.录制按钮.clicked.connect(self.录制信号.emit)
        布局.addWidget(self.录制按钮)

        布局.addWidget(QLabel("速度:"))
        self.速度选择 = QComboBox()
        self.速度选择.addItems(["0.5x", "1x", "2x", "4x"])
        self.速度选择.setCurrentIndex(1)
        布局.addWidget(self.速度选择)

        布局.addWidget(QLabel("循环:"))
        self.循环次数 = QSpinBox()
        self.循环次数.setRange(1, 9999)
        self.循环次数.setValue(1)
        布局.addWidget(self.循环次数)

    def _处理回放(self) -> None:
        """处理回放按钮点击"""
        速度文本 = self.速度选择.currentText()
        速度倍率 = float(速度文本.replace("x", ""))
        self.回放信号.emit(速度倍率, self.循环次数.value())

    def 设置录制状态(self, 录制中: bool) -> None:
        """更新录制按钮状态"""
        self.录制按钮.setText("停止录制" if 录制中 else "录制")

    def 设置回放状态(self, 回放中: bool) -> None:
        """更新回放按钮状态"""
        self.回放按钮.setText("停止回放" if 回放中 else "回放")