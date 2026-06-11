from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget,
    QTreeWidgetItem, QMenu,
)
from PySide6.QtCore import Qt, Signal
from src.公共.数据结构 import 操作步骤数据
from src.公共.枚举定义 import 操作类型枚举
from src.公共.日志管理 import 获取日志管理器


class 操作列表组件类(QWidget):
    """操作列表区组件，支持树状分支显示"""

    步骤选中信号 = Signal(int)
    步骤添加信号 = Signal(str)
    步骤添加分支信号 = Signal(int, str)  # (父步骤标识, 分支类型)
    步骤删除信号 = Signal(int)
    步骤排序信号 = Signal(int, int)
    步骤保存信号 = Signal(object)

    def __init__(self, 步骤管理服务=None, parent=None):
        super().__init__(parent)
        self.步骤管理服务 = 步骤管理服务
        self.当前脚本标识 = 0
        self._步骤树数据: dict[int, dict[str, list]] = {}  # 缓存步骤树数据
        self.日志 = 获取日志管理器("操作列表组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)

        self.步骤树 = QTreeWidget()
        self.步骤树.setHeaderLabels(["序号", "操作类型", "参数摘要", "延时(ms)"])
        self.步骤树.setColumnWidth(0, 60)
        self.步骤树.setColumnWidth(1, 100)
        self.步骤树.setColumnWidth(2, 200)
        self.步骤树.setColumnWidth(3, 60)
        self.步骤树.itemClicked.connect(self._处理步骤选中)
        self.步骤树.itemDoubleClicked.connect(self._处理步骤双击编辑)
        self.步骤树.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.步骤树.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.步骤树.customContextMenuRequested.connect(self._显示右键菜单)
        布局.addWidget(self.步骤树)

    def 加载脚本步骤(self, 脚本标识: int) -> None:
        """加载指定脚本的操作步骤，树状显示"""
        self.当前脚本标识 = 脚本标识
        self.步骤树.clear()
        if not self.步骤管理服务:
            return
        self.步骤管理服务.规范化排序序号(脚本标识)
        顶层步骤列表, 步骤树 = self.步骤管理服务.查询步骤树(脚本标识)
        self._步骤树数据 = 步骤树  # 保存引用供右键菜单使用
        for 步骤 in 顶层步骤列表:
            项 = self._添加步骤项(步骤, 显示序号=步骤.排序序号)
            # 添加子步骤（分支）
            if 步骤.步骤标识 in 步骤树:
                分支字典 = 步骤树[步骤.步骤标识]
                for 分支类型 in ("是", "否"):
                    子步骤列表 = 分支字典.get(分支类型, [])
                    for 子步骤 in 子步骤列表:
                        子项 = self._添加步骤项(子步骤, 显示序号=子步骤.排序序号, 分支前缀=分支类型)
                        项.addChild(子项)

    def 追加录制步骤(self, 步骤: 操作步骤数据) -> None:
        """录制过程中实时追加步骤（仅追加顶层步骤）"""
        显示序号 = 步骤.排序序号 or (self.步骤树.topLevelItemCount() + 1)
        self._添加步骤项(步骤, 显示序号=显示序号)

    def _添加步骤项(self, 步骤: 操作步骤数据, 显示序号: int = 0, 分支前缀: str = "") -> QTreeWidgetItem:
        """添加步骤到列表，返回创建的项"""
        参数摘要 = self._生成参数摘要(步骤)
        if 显示序号 <= 0:
            显示序号 = self.步骤树.topLevelItemCount() + 1
        显示类型 = f"[{分支前缀}] {步骤.操作类型}" if 分支前缀 else 步骤.操作类型
        项 = QTreeWidgetItem([
            str(显示序号),
            显示类型,
            参数摘要,
            str(步骤.步骤延时),
        ])
        项.setData(0, Qt.ItemDataRole.UserRole, 步骤.步骤标识)
        项.setData(0, Qt.ItemDataRole.UserRole + 1, 显示序号)
        if not 分支前缀:
            self.步骤树.addTopLevelItem(项)
        return 项

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
            elif 操作类型 == 操作类型枚举.OCR条件判断:
                return f"({步骤.OCR区域左上角X},{步骤.OCR区域左上角Y})"
        except Exception:
            pass
        return ""

    def _显示右键菜单(self, 位置) -> None:
        """显示右键菜单，支持分支步骤添加"""
        项 = self.步骤树.itemAt(位置)
        菜单 = QMenu(self)
        if 项:
            步骤标识 = 项.data(0, Qt.ItemDataRole.UserRole)
            排序序号 = 项.data(0, Qt.ItemDataRole.UserRole + 1)
            # 判断是否为顶层项
            是顶层 = self.步骤树.indexOfTopLevelItem(项) >= 0
            索引 = self.步骤树.indexOfTopLevelItem(项) if 是顶层 else -1
            # 获取步骤对象以判断操作类型
            步骤对象 = None
            if self.步骤管理服务 and 步骤标识:
                步骤对象 = self.步骤管理服务.步骤DAO.查询ById(步骤标识)
            # 添加操作菜单
            添加菜单 = 菜单.addMenu("添加")
            for 操作类型 in 操作类型枚举:
                添加菜单.addAction(操作类型.value, lambda 类型=操作类型.value: self._打开添加弹窗(类型))
            # 如果是OCR条件判断，添加分支菜单
            if 步骤对象 and 步骤对象.操作类型 == 操作类型枚举.OCR条件判断.value:
                菜单.addSeparator()
                分支菜单 = 菜单.addMenu("添加分支步骤")
                分支菜单.addAction("添加“是”分支步骤", lambda: self._添加分支步骤(步骤标识, "是"))
                分支菜单.addAction("添加“否”分支步骤", lambda: self._添加分支步骤(步骤标识, "否"))
            菜单.addSeparator()
            菜单.addAction("编辑", lambda: self._打开编辑弹窗(步骤标识))
            菜单.addAction("复制", lambda: self._处理复制())
            if 是顶层:
                if 索引 > 0:
                    菜单.addAction("上移", lambda: self.步骤排序信号.emit(排序序号, 排序序号 - 1))
                if 索引 < self.步骤树.topLevelItemCount() - 1:
                    菜单.addAction("下移", lambda: self.步骤排序信号.emit(排序序号, 排序序号 + 1))
            菜单.addSeparator()
            菜单.addAction("删除", lambda: self.步骤删除信号.emit(步骤标识))
        else:
            添加菜单 = 菜单.addMenu("添加")
            for 操作类型 in 操作类型枚举:
                添加菜单.addAction(操作类型.value, lambda 类型=操作类型.value: self._打开添加弹窗(类型))
        菜单.exec(self.步骤树.mapToGlobal(位置))

    def _添加分支步骤(self, 父步骤标识: int, 分支类型: str) -> None:
        """添加分支子步骤"""
        if not self.当前脚本标识 or not self.步骤管理服务:
            return
        from src.表现层.步骤编辑弹窗 import 步骤编辑弹窗类
        # 分支步骤可以是任意操作类型，默认打开操作类型选择
        # 这里简化处理：先弹出操作类型选择
        from PySide6.QtWidgets import QInputDialog
        类型列表 = [e.value for e in 操作类型枚举]
        类型, 确定 = QInputDialog.getItem(self, "添加分支步骤", "选择操作类型:", 类型列表, 0, False)
        if not 确定:
            return
        弹窗 = 步骤编辑弹窗类(类型, parent=self)
        if 弹窗.exec() == 步骤编辑弹窗类.DialogCode.Accepted:
            步骤数据 = 弹窗.收集步骤数据()
            if 步骤数据 and self.步骤管理服务 and self.当前脚本标识:
                self.步骤管理服务.添加步骤(
                    self.当前脚本标识, 步骤数据,
                    父步骤标识=父步骤标识, 分支类型=分支类型
                )
                self.加载脚本步骤(self.当前脚本标识)

    def _打开添加弹窗(self, 操作类型: str) -> None:
        """打开步骤添加弹窗"""
        if not self.当前脚本标识:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请先选中一个脚本")
            return
        from src.表现层.步骤编辑弹窗 import 步骤编辑弹窗类
        弹窗 = 步骤编辑弹窗类(操作类型, parent=self)
        if 弹窗.exec() == 步骤编辑弹窗类.DialogCode.Accepted:
            步骤数据 = 弹窗.收集步骤数据()
            if 步骤数据 and self.步骤管理服务 and self.当前脚本标识:
                self.步骤管理服务.添加步骤(self.当前脚本标识, 步骤数据)
                self.加载脚本步骤(self.当前脚本标识)

    def _打开编辑弹窗(self, 步骤标识: int) -> None:
        """打开步骤编辑弹窗"""
        if not self.步骤管理服务:
            return
        步骤 = self.步骤管理服务.步骤DAO.查询ById(步骤标识)
        if not 步骤:
            return
        from src.表现层.步骤编辑弹窗 import 步骤编辑弹窗类
        弹窗 = 步骤编辑弹窗类(步骤.操作类型, 步骤数据=步骤, parent=self)
        if 弹窗.exec() == 步骤编辑弹窗类.DialogCode.Accepted:
            步骤数据 = 弹窗.收集步骤数据()
            步骤数据.步骤标识 = 步骤标识
            步骤数据.所属脚本标识 = 步骤.所属脚本标识
            步骤数据.排序序号 = 步骤.排序序号
            self.步骤管理服务.修改步骤(步骤标识, 步骤数据)
            self.加载脚本步骤(self.当前脚本标识)

    def _处理复制(self) -> None:
        """处理复制步骤"""
        当前项 = self.步骤树.currentItem()
        if 当前项:
            排序序号 = 当前项.data(0, Qt.ItemDataRole.UserRole + 1)
            步骤标识 = 当前项.data(0, Qt.ItemDataRole.UserRole)
            if 步骤标识 and self.步骤管理服务:
                self.步骤管理服务.复制步骤(步骤标识, 排序序号 + 1)
                self.加载脚本步骤(self.当前脚本标识)

    def _处理步骤选中(self, 项: QTreeWidgetItem, 列: int) -> None:
        """处理步骤选中事件"""
        步骤标识 = 项.data(0, Qt.ItemDataRole.UserRole)
        if 步骤标识:
            self.步骤选中信号.emit(步骤标识)

    def _处理步骤双击编辑(self, 项: QTreeWidgetItem, 列: int) -> None:
        """双击步骤打开编辑弹窗"""
        步骤标识 = 项.data(0, Qt.ItemDataRole.UserRole)
        if 步骤标识:
            self._打开编辑弹窗(步骤标识)
