from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTreeWidget,
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from src.公共.数据结构 import 脚本概要信息
from src.公共.日志管理 import 获取日志管理器


class 脚本列表组件类(QWidget):
    """脚本列表区组件"""

    脚本选中信号 = Signal(int)
    脚本新建信号 = Signal()
    脚本删除信号 = Signal(int)
    脚本复制信号 = Signal(int)
    脚本编辑信号 = Signal(int)
    脚本导出信号 = Signal(int)
    脚本导入信号 = Signal()

    def __init__(self, 脚本管理服务=None, parent=None):
        super().__init__(parent)
        self.脚本管理服务 = 脚本管理服务
        self.当前脚本标识 = 0
        self.日志 = 获取日志管理器("脚本列表组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)
        搜索框布局 = QHBoxLayout()
        self.搜索框 = QLineEdit()
        self.搜索框.setPlaceholderText("搜索脚本...")
        self.搜索框.textChanged.connect(self.执行搜索)
        搜索框布局.addWidget(self.搜索框)
        新建按钮 = QPushButton("新建")
        新建按钮.clicked.connect(self.脚本新建信号.emit)
        搜索框布局.addWidget(新建按钮)
        布局.addLayout(搜索框布局)

        self.脚本树 = QTreeWidget()
        self.脚本树.setHeaderLabels(["脚本名称", "步骤数", "修改时间"])
        self.脚本树.setColumnWidth(0, 150)
        self.脚本树.setColumnWidth(1, 50)
        self.脚本树.setColumnWidth(2, 130)
        self.脚本树.itemClicked.connect(self._处理脚本选中)
        self.脚本树.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.脚本树.customContextMenuRequested.connect(self._显示右键菜单)
        布局.addWidget(self.脚本树)

    def 刷新列表(self) -> None:
        """刷新脚本列表"""
        self.脚本树.clear()
        if not self.脚本管理服务:
            return
        脚本列表 = self.脚本管理服务.查询所有脚本()
        for 脚本 in 脚本列表:
            项 = QTreeWidgetItem([
                脚本.脚本名称,
                str(脚本.步骤数量),
                脚本.修改时间[:19] if 脚本.修改时间 else "",
            ])
            项.setData(0, Qt.ItemDataRole.UserRole, 脚本.脚本标识)
            self.脚本树.addTopLevelItem(项)

    def 执行搜索(self, 关键词: str) -> None:
        """执行脚本搜索"""
        self.脚本树.clear()
        if not self.脚本管理服务:
            return
        if not 关键词:
            脚本列表 = self.脚本管理服务.查询所有脚本()
        else:
            脚本列表 = self.脚本管理服务.按名称搜索(关键词)
        for 脚本 in 脚本列表:
            项 = QTreeWidgetItem([
                脚本.脚本名称,
                str(脚本.步骤数量),
                脚本.修改时间[:19] if 脚本.修改时间 else "",
            ])
            项.setData(0, Qt.ItemDataRole.UserRole, 脚本.脚本标识)
            self.脚本树.addTopLevelItem(项)

    def _处理脚本选中(self, 项: QTreeWidgetItem, 列: int) -> None:
        """处理脚本选中事件"""
        脚本标识 = 项.data(0, Qt.ItemDataRole.UserRole)
        self.当前脚本标识 = 脚本标识
        self.脚本选中信号.emit(脚本标识)

    def _显示右键菜单(self, 位置) -> None:
        """显示右键菜单"""
        项 = self.脚本树.itemAt(位置)
        if not 项:
            return
        脚本标识 = 项.data(0, Qt.ItemDataRole.UserRole)
        菜单 = QMenu(self)
        菜单.addAction("编辑信息", lambda: self.脚本编辑信号.emit(脚本标识))
        菜单.addAction("复制", lambda: self.脚本复制信号.emit(脚本标识))
        菜单.addAction("导出", lambda: self.脚本导出信号.emit(脚本标识))
        菜单.addSeparator()
        菜单.addAction("删除", lambda: self._确认删除(脚本标识))
        菜单.exec(self.脚本树.mapToGlobal(位置))

    def _确认删除(self, 脚本标识: int) -> None:
        """确认删除脚本"""
        回复 = QMessageBox.question(
            self, "确认删除", "确定要删除该脚本吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if 回复 == QMessageBox.StandardButton.Yes:
            self.脚本删除信号.emit(脚本标识)