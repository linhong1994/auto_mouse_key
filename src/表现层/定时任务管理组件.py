from PySide6.QtWidgets import (
    QComboBox, QSpinBox, QTimeEdit, QDateTimeEdit,
    QCheckBox, QDialog, QFormLayout, QDialogButtonBox,
)


class 定时任务对话框(QDialog):
    """定时任务设置对话框，选中脚本后设置定时参数"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置定时任务")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QFormLayout(self)

        self.触发类型选择 = QComboBox()
        self.触发类型选择.addItems(["单次执行", "循环间隔", "每日定时"])
        self.触发类型选择.currentTextChanged.connect(self._切换触发类型)
        布局.addRow("触发类型:", self.触发类型选择)

        self.触发时间输入 = QDateTimeEdit()
        self.触发时间输入.setCalendarPopup(True)
        布局.addRow("触发时间:", self.触发时间输入)

        self.循环间隔输入 = QSpinBox()
        self.循环间隔输入.setRange(1, 1440)
        self.循环间隔输入.setSuffix(" 分钟")
        布局.addRow("循环间隔:", self.循环间隔输入)

        self.每日时间输入 = QTimeEdit()
        布局.addRow("每日时间:", self.每日时间输入)

        self.启用复选框 = QCheckBox("启用")
        self.启用复选框.setChecked(True)
        布局.addRow(self.启用复选框)

        按钮盒 = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        按钮盒.accepted.connect(self.accept)
        按钮盒.rejected.connect(self.reject)
        布局.addRow(按钮盒)

        self._切换触发类型("单次执行")

    def _切换触发类型(self, 类型: str) -> None:
        """切换触发类型时显示/隐藏对应输入"""
        self.触发时间输入.setVisible(类型 == "单次执行")
        self.循环间隔输入.setVisible(类型 == "循环间隔")
        self.每日时间输入.setVisible(类型 == "每日定时")

    def 获取定时配置(self) -> tuple:
        """获取对话框中的定时配置，返回(触发类型, 触发时间, 循环间隔, 每日时间, 启用)"""
        触发类型 = self.触发类型选择.currentText()
        触发时间 = self.触发时间输入.dateTime().toPython().isoformat() if 触发类型 == "单次执行" else None
        循环间隔 = self.循环间隔输入.value() if 触发类型 == "循环间隔" else None
        每日时间 = self.每日时间输入.time().toString("HH:mm") if 触发类型 == "每日定时" else None
        启用 = self.启用复选框.isChecked()
        return (触发类型, 触发时间, 循环间隔, 每日时间, 启用)
