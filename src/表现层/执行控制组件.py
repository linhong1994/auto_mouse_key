from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox, QSpinBox, QLabel
from PySide6.QtCore import Signal
from src.公共.日志管理 import 获取日志管理器


class 执行控制组件类(QWidget):
    """执行控制区组件"""

    回放信号 = Signal(float, int)
    停止回放信号 = Signal()
    紧急停止信号 = Signal()
    录制信号 = Signal()
    热键设置信号 = Signal()
    悬浮窗设置信号 = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.日志 = 获取日志管理器("执行控制组件")
        self._录制键名 = ""
        self._回放键名 = ""
        self._停止回放键名 = ""
        self._紧急停止键名 = ""
        self._回放中 = False
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QHBoxLayout(self)

        self.热键设置按钮 = QPushButton("热键设置")
        self.热键设置按钮.clicked.connect(self.热键设置信号.emit)
        布局.addWidget(self.热键设置按钮)

        self.悬浮窗设置按钮 = QPushButton("悬浮窗设置")
        self.悬浮窗设置按钮.clicked.connect(self.悬浮窗设置信号.emit)
        布局.addWidget(self.悬浮窗设置按钮)

        self.回放按钮 = QPushButton("回放")
        self.回放按钮.clicked.connect(self._处理回放)
        布局.addWidget(self.回放按钮)

        self.紧急停止按钮 = QPushButton("紧急停止")
        self.紧急停止按钮.clicked.connect(self.紧急停止信号.emit)
        布局.addWidget(self.紧急停止按钮)

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
        """处理回放按钮点击，回放中则停止回放，否则启动回放"""
        if self._回放中:
            self.停止回放信号.emit()
        else:
            速度文本 = self.速度选择.currentText()
            速度倍率 = float(速度文本.replace("x", ""))
            self.回放信号.emit(速度倍率, self.循环次数.value())

    def 更新热键按钮文字(self, 热键配置: dict[str, str]) -> None:
        """根据热键配置更新按钮文字，显示对应的热键提示"""
        self._录制键名 = self._格式化热键(热键配置.get("启动录制", "<f9>"))
        self._回放键名 = self._格式化热键(热键配置.get("启动回放", "<f10>"))
        self._停止回放键名 = self._格式化热键(热键配置.get("停止回放", "<f10>"))
        self._紧急停止键名 = self._格式化热键(热键配置.get("紧急停止", "<esc>"))
        if self._回放中:
            self.回放按钮.setText(f"{self._停止回放键名}停止回放")
        else:
            self.回放按钮.setText(f"{self._回放键名}回放")
        self.紧急停止按钮.setText(f"{self._紧急停止键名}紧急停止")
        self.录制按钮.setText(f"{self._录制键名}录制")

    def _格式化热键(self, 热键组合: str) -> str:
        """将热键组合字符串格式化为显示友好的文本

        例: <f9> → F9, <ctrl>+<f9> → Ctrl+F9, <esc> → Esc
        """
        部分列表 = 热键组合.split("+")
        结果 = []
        for 部分 in 部分列表:
            部分 = 部分.strip()
            if 部分.startswith("<") and 部分.endswith(">"):
                键名 = 部分[1:-1]
            else:
                键名 = 部分
            结果.append(键名.capitalize())
        return "+".join(结果)

    def 设置录制状态(self, 录制中: bool) -> None:
        """更新录制按钮状态"""
        if 录制中:
            self.录制按钮.setText(f"{self._录制键名}停止录制")
        else:
            self.录制按钮.setText(f"{self._录制键名}录制")

    def 设置回放状态(self, 回放中: bool) -> None:
        """更新回放按钮状态，回放中切换为停止回放"""
        self._回放中 = 回放中
        if 回放中:
            self.回放按钮.setText(f"{self._停止回放键名}停止回放")
        else:
            self.回放按钮.setText(f"{self._回放键名}回放")

    def 设置回放禁用(self, 禁用: bool) -> None:
        """禁用或启用回放相关控件（定时任务激活时禁用）"""
        self.回放按钮.setDisabled(禁用)
        self.速度选择.setDisabled(禁用)
        self.循环次数.setDisabled(禁用)