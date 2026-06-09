from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QPushButton, QComboBox, QSpinBox,
    QLineEdit, QTimeEdit, QDateTimeEdit, QCheckBox, QDialog,
    QFormLayout, QDialogButtonBox, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from src.公共.数据结构 import 定时任务数据
from src.公共.枚举定义 import 定时触发类型枚举
from src.公共.日志管理 import 获取日志管理器


class 定时任务管理组件类(QWidget):
    """定时任务管理界面"""

    任务变更信号 = Signal()

    def __init__(self, 定时调度器=None, 脚本管理服务=None, parent=None):
        super().__init__(parent)
        self.定时调度器 = 定时调度器
        self.脚本管理服务 = 脚本管理服务
        self.日志 = 获取日志管理器("定时任务管理组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)

        工具栏 = QHBoxLayout()
        新建按钮 = QPushButton("新建任务")
        新建按钮.clicked.connect(self._创建任务)
        工具栏.addWidget(新建按钮)
        删除按钮 = QPushButton("删除任务")
        删除按钮.clicked.connect(self._删除任务)
        工具栏.addWidget(删除按钮)
        刷新按钮 = QPushButton("刷新")
        刷新按钮.clicked.connect(self.刷新列表)
        工具栏.addWidget(刷新按钮)
        布局.addLayout(工具栏)

        self.任务树 = QTreeWidget()
        self.任务树.setHeaderLabels(["任务名称", "关联脚本", "触发类型", "触发规则", "启用", "状态"])
        self.任务树.setColumnWidth(0, 120)
        self.任务树.setColumnWidth(1, 100)
        self.任务树.setColumnWidth(2, 80)
        self.任务树.setColumnWidth(3, 120)
        self.任务树.setColumnWidth(4, 40)
        self.任务树.setColumnWidth(5, 60)
        布局.addWidget(self.任务树)

    def 刷新列表(self) -> None:
        """刷新定时任务列表"""
        self.任务树.clear()
        if not self.定时调度器:
            return
        任务列表 = self.定时调度器.查询所有任务()
        for 任务 in 任务列表:
            触发规则 = self._生成触发规则(任务)
            项 = QTreeWidgetItem([
                任务.任务名称,
                str(任务.关联脚本标识),
                任务.触发类型,
                触发规则,
                "是" if 任务.启用状态 else "否",
                任务.任务状态,
            ])
            项.setData(0, Qt.ItemDataRole.UserRole, 任务.任务标识)
            项.setCheckState(4, Qt.CheckState.Checked if 任务.启用状态 else Qt.CheckState.Unchecked)
            self.任务树.addTopLevelItem(项)

    def _生成触发规则(self, 任务: 定时任务数据) -> str:
        """生成触发规则描述"""
        if 任务.触发类型 == "单次执行":
            return 任务.触发时间 or ""
        elif 任务.触发类型 == "循环间隔":
            return f"每{任务.循环间隔}分钟"
        elif 任务.触发类型 == "每日定时":
            return f"每日{任务.每日时间}"
        return ""

    def _创建任务(self) -> None:
        """创建定时任务"""
        对话框 = 定时任务对话框(self.脚本管理服务, self)
        if 对话框.exec() == QDialog.DialogCode.Accepted:
            任务数据 = 对话框.获取任务数据()
            if self.定时调度器:
                self.定时调度器.创建任务(任务数据)
                self.刷新列表()

    def _删除任务(self) -> None:
        """删除定时任务"""
        当前项 = self.任务树.currentItem()
        if 当前项:
            任务标识 = 当前项.data(0, Qt.ItemDataRole.UserRole)
            回复 = QMessageBox.question(self, "确认删除", "确定要删除该定时任务吗？")
            if 回复 == QMessageBox.StandardButton.Yes:
                self.定时调度器.删除任务(任务标识)
                self.刷新列表()


class 定时任务对话框(QDialog):
    """定时任务创建/编辑对话框"""

    def __init__(self, 脚本管理服务=None, parent=None):
        super().__init__(parent)
        self.脚本管理服务 = 脚本管理服务
        self.setWindowTitle("创建定时任务")
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