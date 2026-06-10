from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QPushButton,
    QLineEdit, QLabel, QDialog, QDialogButtonBox,
)
from PySide6.QtCore import Signal
from src.公共.异常定义 import 热键冲突异常
from src.公共.日志管理 import 获取日志管理器


class 热键设置组件类(QDialog):
    """热键设置界面"""

    配置保存信号 = Signal()

    def __init__(self, 热键管理器=None, parent=None):
        super().__init__(parent)
        self.热键管理器 = 热键管理器
        self.日志 = 获取日志管理器("热键设置组件")
        self.热键输入框: dict[str, QLineEdit] = {}
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)
        表单 = QFormLayout()

        功能列表 = ["启动录制", "停止录制", "启动回放", "停止回放", "紧急停止"]
        当前配置 = self.热键管理器.获取当前配置() if self.热键管理器 else {}

        for 功能 in 功能列表:
            输入框 = QLineEdit()
            输入框.setReadOnly(True)
            输入框.setText(当前配置.get(功能, ""))
            输入框.setPlaceholderText("点击设置热键...")
            输入框.mousePressEvent = lambda 事件, f=功能, i=输入框: self._开始录制热键(f, i)
            self.热键输入框[功能] = 输入框
            表单.addRow(f"{功能}:", 输入框)

        布局.addLayout(表单)

        保存按钮 = QPushButton("保存热键配置")
        保存按钮.clicked.connect(self._保存配置)
        布局.addWidget(保存按钮)

    def _开始录制热键(self, 功能名称: str, 输入框: QLineEdit) -> None:
        """开始录制热键输入"""
        输入框.setText("按下热键...")
        try:
            from pynput import keyboard
            def 按键回调(按键):
                按键名称 = self._获取按键名称(按键)
                if 按键名称:
                    输入框.setText(按键名称)
                监听器.stop()
                return False
            监听器 = keyboard.Listener(on_press=按键回调)
            监听器.start()
        except Exception as 异常:
            self.日志.error(f"热键录制失败: {异常}")
            输入框.setText("")

    def _获取按键名称(self, 按键) -> str | None:
        """获取按键名称"""
        try:
            from pynput import keyboard
            if isinstance(按键, keyboard.Key):
                return f"<{按键.name}>"
            elif isinstance(按键, keyboard.KeyCode):
                return 按键.char if 按键.char else str(按键)
        except Exception:
            pass
        return None

    def _保存配置(self) -> None:
        """保存热键配置"""
        if not self.热键管理器:
            return
        for 功能名称, 输入框 in self.热键输入框.items():
            热键组合 = 输入框.text()
            if 热键组合:
                try:
                    self.热键管理器.注册热键(功能名称, 热键组合)
                except 热键冲突异常 as 异常:
                    self.日志.warning(str(异常))
        self.热键管理器.保存配置()
        self.配置保存信号.emit()