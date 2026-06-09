from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QMouseEvent
from src.公共.数据结构 import 悬浮窗日志条目, 步骤预览信息
from src.公共.枚举定义 import 运行状态枚举
from src.公共.日志管理 import 获取日志管理器


class 悬浮窗类(QWidget):
    """悬浮窗组件，置顶显示运行状态与日志"""

    紧急停止信号 = Signal()

    def __init__(self, 执行引擎=None, 配置DAO=None, parent=None):
        super().__init__(parent)
        self.执行引擎 = 执行引擎
        self.配置DAO = 配置DAO
        self._展开 = True
        self._日志条目列表: list[悬浮窗日志条目] = []
        self._日志上限 = 200
        self._拖拽偏移 = None
        self.日志 = 获取日志管理器("悬浮窗")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setFixedSize(300, 200 if self._展开 else 40)
        self.setWindowOpacity(1.0)

        主布局 = QVBoxLayout(self)
        主布局.setContentsMargins(4, 4, 4, 4)
        主布局.setSpacing(2)

        状态栏布局 = QHBoxLayout()
        self.展开收起按钮 = QPushButton("收起")
        self.展开收起按钮.setFixedWidth(40)
        self.展开收起按钮.clicked.connect(self._切换展开收起)
        状态栏布局.addWidget(self.展开收起按钮)

        self.状态指示灯 = QLabel("●")
        self.状态指示灯.setStyleSheet("color: gray; font-size: 14px;")
        状态栏布局.addWidget(self.状态指示灯)

        self.状态文本 = QLabel("空闲")
        self.状态文本.setStyleSheet("font-weight: bold;")
        状态栏布局.addWidget(self.状态文本)

        self.进度文本 = QLabel("")
        状态栏布局.addWidget(self.进度文本)

        状态栏布局.addStretch()

        self.紧急停止按钮 = QPushButton("紧急停止")
        self.紧急停止按钮.setStyleSheet("background-color: #ff4444; color: white;")
        self.紧急停止按钮.clicked.connect(self.紧急停止信号.emit)
        状态栏布局.addWidget(self.紧急停止按钮)

        主布局.addLayout(状态栏布局)

        self.日志区 = QTextEdit()
        self.日志区.setReadOnly(True)
        self.日志区.setMaximumHeight(100)
        self.日志区.setStyleSheet("font-size: 11px;")
        主布局.addWidget(self.日志区)

        self.预览区 = QTextEdit()
        self.预览区.setReadOnly(True)
        self.预览区.setMaximumHeight(50)
        self.预览区.setStyleSheet("font-size: 11px;")
        主布局.addWidget(self.预览区)

    def 开启悬浮窗(self) -> None:
        """创建并显示悬浮窗"""
        self._加载位置配置()
        self.show()

    def 关闭悬浮窗(self) -> None:
        """关闭并销毁悬浮窗"""
        self._保存位置配置()
        self.close()

    def 展开窗口(self) -> None:
        """展开悬浮窗，显示完整信息区域"""
        self._展开 = True
        self.展开收起按钮.setText("收起")
        self.日志区.setVisible(True)
        self.预览区.setVisible(True)
        self.setFixedSize(300, 200)

    def 收起窗口(self) -> None:
        """收起悬浮窗，仅显示运行状态摘要"""
        self._展开 = False
        self.展开收起按钮.setText("展开")
        self.日志区.setVisible(False)
        self.预览区.setVisible(False)
        self.setFixedSize(300, 40)

    def 更新运行状态(self, 状态: 运行状态枚举, 进度: str = "") -> None:
        """更新运行状态显示"""
        颜色映射 = {
            运行状态枚举.空闲: "gray",
            运行状态枚举.录制中: "orange",
            运行状态枚举.回放中: "green",
            运行状态枚举.定时等待: "blue",
            运行状态枚举.已暂停: "yellow",
            运行状态枚举.执行失败: "red",
        }
        颜色 = 颜色映射.get(状态, "gray")
        self.状态指示灯.setStyleSheet(f"color: {颜色}; font-size: 14px;")
        self.状态文本.setText(状态.value)
        self.进度文本.setText(进度)

    def 追加运行日志(self, 日志条目: 悬浮窗日志条目) -> None:
        """追加一条运行日志"""
        self._日志条目列表.append(日志条目)
        if len(self._日志条目列表) > self._日志上限:
            self._日志条目列表 = self._日志条目列表[-self._日志上限:]
        文本行 = f"{日志条目.日志时间戳} {日志条目.操作描述} {日志条目.执行结果}"
        if 日志条目.附加信息:
            文本行 += f" ({日志条目.附加信息})"
        self.日志区.append(文本行)

    def 更新即将运行操作(self, 步骤预览列表: list[步骤预览信息]) -> None:
        """更新即将运行操作预览"""
        self.预览区.clear()
        for 预览 in 步骤预览列表:
            self.预览区.append(f"{预览.步骤序号}. {预览.操作类型} {预览.参数摘要}")

    def 设置透明度(self, 透明度百分比: int) -> None:
        """设置悬浮窗透明度"""
        self.setWindowOpacity(透明度百分比 / 100.0)

    def 检测操作区域冲突(self, 目标坐标X: int, 目标坐标Y: int) -> bool:
        """检测操作目标是否位于悬浮窗区域内"""
        窗口位置 = self.geometry()
        return 窗口位置.contains(目标坐标X, 目标坐标Y)

    def 自动避让(self) -> None:
        """临时隐藏悬浮窗（自动避让）"""
        self.hide()

    def 恢复显示(self) -> None:
        """恢复悬浮窗显示"""
        self.show()

    def _切换展开收起(self) -> None:
        """切换展开/收起状态"""
        if self._展开:
            self.收起窗口()
        else:
            self.展开窗口()

    def _加载位置配置(self) -> None:
        """从配置加载悬浮窗位置"""
        if not self.配置DAO:
            return
        try:
            X = int(self.配置DAO.查询配置("悬浮窗位置X", "-1"))
            Y = int(self.配置DAO.查询配置("悬浮窗位置Y", "-1"))
            透明度 = int(self.配置DAO.查询配置("悬浮窗透明度", "100"))
            if X >= 0 and Y >= 0:
                self.move(X, Y)
            self.setWindowOpacity(透明度 / 100.0)
            展开配置 = self.配置DAO.查询配置("悬浮窗展开", "true")
            if 展开配置 == "false":
                self.收起窗口()
        except Exception:
            pass

    def _保存位置配置(self) -> None:
        """保存悬浮窗位置到配置"""
        if not self.配置DAO:
            return
        try:
            self.配置DAO.设置配置("悬浮窗位置X", str(self.x()))
            self.配置DAO.设置配置("悬浮窗位置Y", str(self.y()))
            self.配置DAO.设置配置("悬浮窗展开", "true" if self._展开 else "false")
        except Exception:
            pass

    def mousePressEvent(self, 事件: QMouseEvent) -> None:
        """鼠标按下事件，开始拖拽"""
        if 事件.button() == Qt.MouseButton.LeftButton:
            self._拖拽偏移 = 事件.position().toPoint()

    def mouseMoveEvent(self, 事件: QMouseEvent) -> None:
        """鼠标移动事件，拖拽移动窗口"""
        if self._拖拽偏移 is not None:
            self.move(事件.globalPosition().toPoint() - self._拖拽偏移)

    def mouseReleaseEvent(self, 事件: QMouseEvent) -> None:
        """鼠标释放事件，结束拖拽"""
        self._拖拽偏移 = None