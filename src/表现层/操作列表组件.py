from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QPushButton, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from src.公共.数据结构 import 操作步骤数据
from src.公共.枚举定义 import 操作类型枚举
from src.公共.日志管理 import 获取日志管理器


class 操作列表组件类(QWidget):
    """操作列表区组件"""

    步骤选中信号 = Signal(int)
    步骤添加信号 = Signal(str)
    步骤删除信号 = Signal(int)
    步骤排序信号 = Signal(int, int)

    def __init__(self, 步骤管理服务=None, parent=None):
        super().__init__(parent)
        self.步骤管理服务 = 步骤管理服务
        self.当前脚本标识 = 0
        self.日志 = 获取日志管理器("操作列表组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)

        工具栏布局 = QHBoxLayout()
        self.添加类型选择 = QComboBox()
        for 操作类型 in 操作类型枚举:
            self.添加类型选择.addItem(操作类型.value)
        工具栏布局.addWidget(self.添加类型选择)
        添加按钮 = QPushButton("添加")
        添加按钮.clicked.connect(self._处理添加)
        工具栏布局.addWidget(添加按钮)
        删除按钮 = QPushButton("删除")
        删除按钮.clicked.connect(self._处理删除)
        工具栏布局.addWidget(删除按钮)
        上移按钮 = QPushButton("上移")
        上移按钮.clicked.connect(self._处理上移)
        工具栏布局.addWidget(上移按钮)
        下移按钮 = QPushButton("下移")
        下移按钮.clicked.connect(self._处理下移)
        工具栏布局.addWidget(下移按钮)
        复制按钮 = QPushButton("复制")
        复制按钮.clicked.connect(self._处理复制)
        工具栏布局.addWidget(复制按钮)
        布局.addLayout(工具栏布局)

        self.步骤树 = QTreeWidget()
        self.步骤树.setHeaderLabels(["序号", "操作类型", "参数摘要", "延时(ms)"])
        self.步骤树.setColumnWidth(0, 40)
        self.步骤树.setColumnWidth(1, 100)
        self.步骤树.setColumnWidth(2, 200)
        self.步骤树.setColumnWidth(3, 60)
        self.步骤树.itemClicked.connect(self._处理步骤选中)
        self.步骤树.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        布局.addWidget(self.步骤树)

    def 加载脚本步骤(self, 脚本标识: int) -> None:
        """加载指定脚本的操作步骤"""
        self.当前脚本标识 = 脚本标识
        self.步骤树.clear()
        if not self.步骤管理服务:
            return
        步骤列表 = self.步骤管理服务.查询脚本步骤(脚本标识)
        for 步骤 in 步骤列表:
            self._添加步骤项(步骤)

    def 追加录制步骤(self, 步骤: 操作步骤数据) -> None:
        """录制过程中实时追加步骤"""
        self._添加步骤项(步骤)

    def _添加步骤项(self, 步骤: 操作步骤数据) -> None:
        """添加步骤到列表"""
        参数摘要 = self._生成参数摘要(步骤)
        项 = QTreeWidgetItem([
            str(步骤.排序序号),
            步骤.操作类型,
            参数摘要,
            str(步骤.步骤延时),
        ])
        项.setData(0, Qt.ItemDataRole.UserRole, 步骤.步骤标识)
        self.步骤树.addTopLevelItem(项)

    def _生成参数摘要(self, 步骤: 操作步骤数据) -> str:
        """生成步骤参数摘要"""
        try:
            操作类型 = 操作类型枚举(步骤.操作类型)
            from src.公共.枚举定义 import 鼠标操作类型集合, 按键操作类型集合
            if 鼠标操作类型集合.包含(操作类型):
                return f"({步骤.目标坐标X}, {步骤.目标坐标Y})"
            elif 按键操作类型集合.包含(操作类型):
                return 步骤.按键值 or 步骤.输入文本 or ""
            elif 操作类型 == 操作类型枚举.延时:
                return f"{步骤.延时时长}ms"
            elif 操作类型 in (操作类型枚举.OCR识别, 操作类型枚举.OCR条件判断):
                return f"({步骤.OCR区域左上角X},{步骤.OCR区域左上角Y})"
        except Exception:
            pass
        return ""

    def _处理添加(self) -> None:
        """处理添加步骤"""
        操作类型 = self.添加类型选择.currentText()
        self.步骤添加信号.emit(操作类型)

    def _处理删除(self) -> None:
        """处理删除步骤"""
        当前项 = self.步骤树.currentItem()
        if 当前项:
            步骤标识 = 当前项.data(0, Qt.ItemDataRole.UserRole)
            if 步骤标识:
                self.步骤删除信号.emit(步骤标识)

    def _处理上移(self) -> None:
        """处理上移步骤"""
        当前项 = self.步骤树.currentItem()
        if 当前项:
            索引 = self.步骤树.indexOfTopLevelItem(当前项)
            if 索引 > 0:
                self.步骤排序信号.emit(索引 + 1, 索引)

    def _处理下移(self) -> None:
        """处理下移步骤"""
        当前项 = self.步骤树.currentItem()
        if 当前项:
            索引 = self.步骤树.indexOfTopLevelItem(当前项)
            if 索引 < self.步骤树.topLevelItemCount() - 1:
                self.步骤排序信号.emit(索引 + 1, 索引 + 2)

    def _处理复制(self) -> None:
        """处理复制步骤"""
        当前项 = self.步骤树.currentItem()
        if 当前项:
            索引 = self.步骤树.indexOfTopLevelItem(当前项) + 1
            步骤标识 = 当前项.data(0, Qt.ItemDataRole.UserRole)
            if 步骤标识 and self.步骤管理服务:
                self.步骤管理服务.复制步骤(步骤标识, 索引)
                self.加载脚本步骤(self.当前脚本标识)

    def _处理步骤选中(self, 项: QTreeWidgetItem, 列: int) -> None:
        """处理步骤选中事件"""
        步骤标识 = 项.data(0, Qt.ItemDataRole.UserRole)
        if 步骤标识:
            self.步骤选中信号.emit(步骤标识)