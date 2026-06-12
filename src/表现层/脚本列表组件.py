from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTreeWidget,
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QTimer
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
    设置定时任务信号 = Signal(int)    # 参数：脚本标识
    停止定时任务信号 = Signal()

    def __init__(self, 脚本管理服务=None, parent=None):
        super().__init__(parent)
        self.脚本管理服务 = 脚本管理服务
        self.当前脚本标识 = 0
        self._当前运行脚本标识 = 0
        self._当前运行状态文本 = "空闲"
        # 定时任务状态跟踪
        self._定时任务脚本标识: int = 0
        self._定时任务标识: int = 0
        self._定时下次触发时间 = None   # datetime对象
        self._定时触发类型: str = ""
        self._定时循环间隔: int = 0
        self._定时每日时间: str = ""
        self.日志 = 获取日志管理器("脚本列表组件")
        self.初始化界面()
        # 倒计时更新定时器
        self._倒计时定时器 = QTimer(self)
        self._倒计时定时器.timeout.connect(self._更新倒计时)
        self._倒计时定时器.setInterval(1000)

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)
        self.搜索框 = QLineEdit()
        self.搜索框.setPlaceholderText("搜索脚本...")
        self.搜索框.textChanged.connect(self.执行搜索)
        布局.addWidget(self.搜索框)

        self.脚本树 = QTreeWidget()
        self.脚本树.setHeaderLabels(["脚本名称", "步骤数", "状态", "修改时间"])
        self.脚本树.setColumnWidth(0, 150)
        self.脚本树.setColumnWidth(1, 50)
        self.脚本树.setColumnWidth(2, 60)
        self.脚本树.setColumnWidth(3, 130)
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
            状态文本 = self._获取状态文本(脚本.脚本标识)
            项 = QTreeWidgetItem([
                脚本.脚本名称,
                str(脚本.步骤数量),
                状态文本,
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
            状态文本 = self._获取状态文本(脚本.脚本标识)
            项 = QTreeWidgetItem([
                脚本.脚本名称,
                str(脚本.步骤数量),
                状态文本,
                脚本.修改时间[:19] if 脚本.修改时间 else "",
            ])
            项.setData(0, Qt.ItemDataRole.UserRole, 脚本.脚本标识)
            self.脚本树.addTopLevelItem(项)

    def _获取状态文本(self, 脚本标识: int) -> str:
        """获取指定脚本的状态文本，综合考虑运行状态和定时任务状态"""
        if 脚本标识 == self._当前运行脚本标识 and self._当前运行状态文本 != "空闲":
            return self._当前运行状态文本
        if 脚本标识 == self._定时任务脚本标识:
            return "定时中..."
        return "空闲"

    def 设置定时任务状态(self, 脚本标识: int, 任务标识: int, 任务数据=None) -> None:
        """设置定时任务状态，启动倒计时显示"""
        from datetime import datetime
        self._定时任务脚本标识 = 脚本标识
        self._定时任务标识 = 任务标识
        if 任务数据:
            self._定时触发类型 = 任务数据.触发类型
            self._定时循环间隔 = 任务数据.循环间隔 or 0
            self._定时每日时间 = 任务数据.每日时间 or ""
            # 计算下次触发时间
            if 任务数据.触发类型 == "单次执行" and 任务数据.触发时间:
                self._定时下次触发时间 = datetime.fromisoformat(任务数据.触发时间)
            elif 任务数据.触发类型 == "循环间隔" and 任务数据.循环间隔:
                from datetime import timedelta
                self._定时下次触发时间 = datetime.now() + timedelta(minutes=任务数据.循环间隔)
            elif 任务数据.触发类型 == "每日定时" and 任务数据.每日时间:
                时, 分 = map(int, 任务数据.每日时间.split(":"))
                今日触发 = datetime.now().replace(hour=时, minute=分, second=0, microsecond=0)
                if 今日触发 > datetime.now():
                    self._定时下次触发时间 = 今日触发
                else:
                    from datetime import timedelta
                    self._定时下次触发时间 = 今日触发 + timedelta(days=1)
        self._倒计时定时器.start()
        self.刷新列表()

    def 清除定时状态(self) -> None:
        """清除定时任务状态，停止倒计时"""
        self._倒计时定时器.stop()
        self._定时任务脚本标识 = 0
        self._定时任务标识 = 0
        self._定时下次触发时间 = None
        self._定时触发类型 = ""
        self._定时循环间隔 = 0
        self._定时每日时间 = ""
        self.刷新列表()

    def _更新倒计时(self) -> None:
        """每秒更新倒计时显示"""
        from datetime import datetime, timedelta
        if not self._定时任务脚本标识 or not self._定时下次触发时间:
            return
        现在 = datetime.now()
        剩余 = self._定时下次触发时间 - 现在
        if 剩余.total_seconds() <= 0:
            # 倒计时结束，计算下次触发（循环间隔/每日定时）
            if self._定时触发类型 == "循环间隔" and self._定时循环间隔:
                self._定时下次触发时间 = 现在 + timedelta(minutes=self._定时循环间隔)
                剩余 = self._定时下次触发时间 - 现在
            elif self._定时触发类型 == "每日定时" and self._定时每日时间:
                self._定时下次触发时间 = self._定时下次触发时间 + timedelta(days=1)
                剩余 = self._定时下次触发时间 - 现在
            else:
                倒计时文本 = "即将执行"
                self._更新定时状态列(倒计时文本)
                return
        总秒数 = int(剩余.total_seconds())
        时 = 总秒数 // 3600
        分 = (总秒数 % 3600) // 60
        秒 = 总秒数 % 60
        if 时 > 0:
            倒计时文本 = f"定时 {时}时{分}分{秒}秒"
        elif 分 > 0:
            倒计时文本 = f"定时 {分}分{秒}秒"
        else:
            倒计时文本 = f"定时 {秒}秒"
        self._更新定时状态列(倒计时文本)

    def _更新定时状态列(self, 状态文本: str) -> None:
        """更新脚本列表中定时任务脚本的状态列"""
        根节点 = self.脚本树.invisibleRootItem()
        for i in range(根节点.childCount()):
            项 = 根节点.child(i)
            项标识 = 项.data(0, Qt.ItemDataRole.UserRole)
            if 项标识 == self._定时任务脚本标识:
                项.setText(2, 状态文本)

    def _处理脚本选中(self, 项: QTreeWidgetItem, 列: int) -> None:
        """处理脚本选中事件"""
        脚本标识 = 项.data(0, Qt.ItemDataRole.UserRole)
        self.当前脚本标识 = 脚本标识
        self.脚本选中信号.emit(脚本标识)

    def 更新脚本运行状态(self, 脚本标识: int, 状态文本: str) -> None:
        """更新指定脚本的运行状态显示"""
        self._当前运行脚本标识 = 脚本标识
        self._当前运行状态文本 = 状态文本
        # 更新当前显示列表中对应脚本的状态列
        根节点 = self.脚本树.invisibleRootItem()
        for i in range(根节点.childCount()):
            项 = 根节点.child(i)
            项标识 = 项.data(0, Qt.ItemDataRole.UserRole)
            if 项标识 == 脚本标识:
                项.setText(2, 状态文本)
            elif 项.text(2) != "空闲":
                项.setText(2, "空闲")

    def _显示右键菜单(self, 位置) -> None:
        """显示右键菜单"""
        项 = self.脚本树.itemAt(位置)
        菜单 = QMenu(self)
        if 项:
            脚本标识 = 项.data(0, Qt.ItemDataRole.UserRole)
            菜单.addAction("新建", lambda: self.脚本新建信号.emit())
            菜单.addAction("导入", lambda: self.脚本导入信号.emit())
            菜单.addSeparator()
            菜单.addAction("编辑", lambda: self.脚本编辑信号.emit(脚本标识))
            菜单.addAction("复制", lambda: self.脚本复制信号.emit(脚本标识))
            菜单.addAction("导出", lambda: self.脚本导出信号.emit(脚本标识))
            菜单.addSeparator()
            # 定时任务菜单项逻辑：
            # - 已设置定时的脚本：显示“停止定时”
            # - 无全局定时任务时：所有脚本显示“定时任务”
            # - 其他脚本已设置定时任务时：不显示定时相关选项
            if self._定时任务脚本标识 == 脚本标识:
                菜单.addAction("停止定时", lambda: self.停止定时任务信号.emit())
            elif self._定时任务脚本标识 == 0:
                菜单.addAction("定时任务", lambda: self.设置定时任务信号.emit(脚本标识))
            菜单.addSeparator()
            菜单.addAction("删除", lambda: self._确认删除(脚本标识))
        else:
            菜单.addAction("新建", lambda: self.脚本新建信号.emit())
            菜单.addAction("导入", lambda: self.脚本导入信号.emit())
        菜单.exec(self.脚本树.mapToGlobal(位置))

    def _确认删除(self, 脚本标识: int) -> None:
        """确认删除脚本"""
        回复 = QMessageBox.question(
            self, "确认删除", "确定要删除该脚本吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if 回复 == QMessageBox.StandardButton.Yes:
            self.脚本删除信号.emit(脚本标识)