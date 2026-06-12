from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QToolBar,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from src.公共.枚举定义 import 运行状态枚举
from src.公共.日志管理 import 获取日志管理器


class 主窗口类(QMainWindow):
    """应用主窗口，包含五大交互区域"""

    def __init__(self):
        super().__init__()
        self.脚本列表组件 = None
        self.操作列表组件 = None
        self.步骤详情组件 = None

        self.执行控制组件 = None
        self.悬浮窗 = None
        self.系统托盘 = None
        self.热键管理器 = None
        self._菜单动作 = []
        self.日志 = 获取日志管理器("主窗口")

    def 初始化界面(self) -> None:
        """初始化主界面布局和各区域组件"""
        self.setWindowTitle("自动操作工具")
        self.setMinimumSize(1000, 600)
        self.初始化菜单栏()
        self.初始化中央区域()
        self.初始化状态栏()

    def 初始化菜单栏(self) -> None:
        """初始化菜单栏"""
        菜单栏 = self.menuBar()

        设置菜单 = 菜单栏.addMenu("设置")
        热键动作 = QAction("热键设置", self)
        悬浮窗动作 = QAction("悬浮窗设置", self)
        设置菜单.addAction(热键动作)
        设置菜单.addAction(悬浮窗动作)

        self._菜单动作 = [
            热键动作, 悬浮窗动作,
        ]
        self._菜单对象 = [设置菜单]

    def 初始化中央区域(self) -> None:
        """初始化中央区域布局：左-脚本列表，右-（控制栏 + 操作列表+详情）"""
        中央组件 = QWidget()
        主布局 = QHBoxLayout(中央组件)

        # 顶部控制栏：执行控制按钮
        顶部布局 = QHBoxLayout()
        顶部布局.setContentsMargins(0, 0, 0, 0)
        if self.执行控制组件:
            顶部布局.addWidget(self.执行控制组件)
        顶部组件 = QWidget()
        顶部组件.setLayout(顶部布局)

        # 下方分割区：左-操作列表，右-步骤详情
        下方分割器 = QSplitter(Qt.Orientation.Horizontal)
        if self.操作列表组件:
            下方分割器.addWidget(self.操作列表组件)
        if self.步骤详情组件:
            下方分割器.addWidget(self.步骤详情组件)
        下方分割器.setStretchFactor(0, 3)
        下方分割器.setStretchFactor(1, 1)
        下方分割器.setSizes([500, 200])

        # 右侧整体：顶部控制栏 + 下方分割区，垂直堆叠
        右侧布局 = QVBoxLayout()
        右侧布局.setContentsMargins(0, 0, 0, 0)
        右侧布局.addWidget(顶部组件)
        右侧布局.addWidget(下方分割器, 1)
        右侧组件 = QWidget()
        右侧组件.setLayout(右侧布局)

        主分割器 = QSplitter(Qt.Orientation.Horizontal)
        if self.脚本列表组件:
            主分割器.addWidget(self.脚本列表组件)
        主分割器.addWidget(右侧组件)
        主分割器.setStretchFactor(0, 1)
        主分割器.setStretchFactor(1, 3)
        主分割器.setSizes([420, 580])

        主布局.addWidget(主分割器)
        self.setCentralWidget(中央组件)

    def 初始化状态栏(self) -> None:
        """初始化状态栏"""
        self.状态栏 = QStatusBar()
        self.setStatusBar(self.状态栏)
        self.状态栏.showMessage("就绪")

    def 更新执行状态显示(self, 状态: 运行状态枚举, 进度: str) -> None:
        """更新执行状态和进度显示"""
        self.状态栏.showMessage(f"状态: {状态.value} {进度}")
