from PySide6.QtWidgets import (
    QComboBox, QSpinBox, QLineEdit, QTimeEdit, QDateTimeEdit,
    QCheckBox, QDialog, QFormLayout, QDialogButtonBox,
)
from src.公共.数据结构 import 定时任务数据


class 定时任务对话框(QDialog):
    """定时任务创建/编辑对话框"""

    def __init__(self, 脚本管理服务=None, parent=None, 默认脚本标识: int = 0):
        super().__init__(parent)
        self.脚本管理服务 = 脚本管理服务
        self.默认脚本标识 = 默认脚本标识
        self.setWindowTitle("设置定时任务")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QFormLayout(self)

        self.任务名称输入 = QLineEdit()
        布局.addRow("任务名称:", self.任务名称输入)

        self.脚本选择 = QComboBox()
        if self.脚本管理服务:
            脚本列表 = self.脚本管理服务.查询所有脚本()
            for 脚本 in 脚本列表:
                self.脚本选择.addItem(脚本.脚本名称, 脚本.脚本标识)
            # 预选默认脚本
            if self.默认脚本标识:
                for i in range(self.脚本选择.count()):
                    if self.脚本选择.itemData(i) == self.默认脚本标识:
                        self.脚本选择.setCurrentIndex(i)
                        break
        布局.addRow("关联脚本:", self.脚本选择)

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

    def 获取任务数据(self) -> 定时任务数据:
        """获取对话框中的任务数据"""
        return 定时任务数据(
            任务名称=self.任务名称输入.text(),
            关联脚本标识=self.脚本选择.currentData() or 0,
            触发类型=self.触发类型选择.currentText(),
            触发时间=self.触发时间输入.dateTime().toPython().isoformat() if self.触发类型选择.currentText() == "单次执行" else None,
            循环间隔=self.循环间隔输入.value() if self.触发类型选择.currentText() == "循环间隔" else None,
            每日时间=self.每日时间输入.time().toString("HH:mm") if self.触发类型选择.currentText() == "每日定时" else None,
            启用状态=self.启用复选框.isChecked(),
        )
