from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
    QLineEdit, QComboBox, QPushButton, QStackedWidget,
    QHBoxLayout, QLabel, QDialogButtonBox,
)
from PySide6.QtCore import Qt, Signal, QTimer
from src.公共.数据结构 import 操作步骤数据
from src.公共.枚举定义 import 操作类型枚举, 鼠标操作类型集合, 按键操作类型集合
from src.公共.日志管理 import 获取日志管理器


class 步骤编辑弹窗类(QDialog):
    """步骤编辑弹窗，根据操作类型动态显示参数配置，支持坐标捕获"""

    _坐标捕获完成信号 = Signal(int, int)
    _区域选中完成信号 = Signal(int, int, int, int)  # 左上X, 左上Y, 右下X, 右下Y
    _捕获取消信号 = Signal()

    区域选择返回码 = 10  # 自定义返回码，表示需要进行区域框选

    def __init__(self, 操作类型: str, 步骤数据: 操作步骤数据 | None = None,
                 待填充区域: tuple | None = None, 脚本管理服务=None,
                 当前脚本标识: int = 0, parent=None):
        super().__init__(parent)
        self.操作类型 = 操作类型
        self.步骤数据 = 步骤数据
        self._待填充区域 = 待填充区域
        self.脚本管理服务 = 脚本管理服务
        self.当前脚本标识 = 当前脚本标识
        self.日志 = 获取日志管理器("步骤编辑弹窗")
        self.坐标浮窗 = None
        self._待捕获目标 = None
        self._鼠标监听器 = None
        self._主窗口 = None
        self._原位置 = None
        self._坐标捕获完成信号.connect(self._处理全局捕获结果)
        self._区域选中完成信号.connect(self._处理区域选中)
        self._捕获取消信号.connect(self._取消捕获)
        self._区域框选浮窗 = None
        self._框选前数据 = None
        self._框选结果区域 = None
        self._框选已完成 = False
        self.初始化界面()
        if 步骤数据:
            self._加载已有数据(步骤数据)
        if 待填充区域:
            self._填充区域坐标(待填充区域)

    def 初始化界面(self) -> None:
        """初始化界面"""
        self.setWindowTitle(f"编辑步骤 - {self.操作类型}")
        self.setMinimumWidth(360)
        布局 = QVBoxLayout(self)

        类型标签 = QLabel(f"操作类型: {self.操作类型}")
        类型标签.setStyleSheet("font-weight: bold; font-size: 14px;")
        布局.addWidget(类型标签)

        self.堆叠组件 = QStackedWidget()
        self._创建鼠标配置页()      # index 0
        self._创建按键配置页()      # index 1
        self._创建OCR条件配置页()   # index 2（合并区域+条件）
        self._创建延时配置页()      # index 3
        self._创建拖拽配置页()      # index 4
        self._创建调用脚本配置页()  # index 5
        布局.addWidget(self.堆叠组件)

        self._切换配置页()

        按钮盒 = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        按钮盒.accepted.connect(self.accept)
        按钮盒.rejected.connect(self.reject)
        布局.addWidget(按钮盒)

    def _切换配置页(self) -> None:
        """根据操作类型切换配置页"""
        try:
            类型 = 操作类型枚举(self.操作类型)
            if 类型 == 操作类型枚举.鼠标拖拽:
                self.堆叠组件.setCurrentIndex(4)
            elif 鼠标操作类型集合.包含(类型):
                self.堆叠组件.setCurrentIndex(0)
            elif 按键操作类型集合.包含(类型):
                self.堆叠组件.setCurrentIndex(1)
            elif 类型 == 操作类型枚举.OCR条件判断:
                self.堆叠组件.setCurrentIndex(2)
            elif 类型 == 操作类型枚举.延时:
                self.堆叠组件.setCurrentIndex(3)
            elif 类型 == 操作类型枚举.调用脚本:
                self.堆叠组件.setCurrentIndex(5)
        except Exception:
            self.堆叠组件.setCurrentIndex(3)

    def _创建鼠标配置页(self) -> None:
        """创建鼠标操作配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        坐标布局 = QHBoxLayout()
        self.鼠标坐标X = QSpinBox()
        self.鼠标坐标X.setRange(0, 9999)
        坐标布局.addWidget(self.鼠标坐标X)
        self.鼠标坐标Y = QSpinBox()
        self.鼠标坐标Y.setRange(0, 9999)
        坐标布局.addWidget(self.鼠标坐标Y)
        捕获按钮 = QPushButton("捕获坐标")
        捕获按钮.clicked.connect(lambda: self._启动坐标捕获("鼠标"))
        坐标布局.addWidget(捕获按钮)
        表单.addRow("坐标X/Y:", 坐标布局)
        self.鼠标延时 = QSpinBox()
        self.鼠标延时.setRange(0, 60000)
        self.鼠标延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.鼠标延时)
        self.堆叠组件.addWidget(页)

    def _创建按键配置页(self) -> None:
        """创建按键操作配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        self.按键值输入 = QLineEdit()
        表单.addRow("按键值:", self.按键值输入)
        self.修饰键输入 = QLineEdit()
        self.修饰键输入.setPlaceholderText("如: ctrl+shift")
        表单.addRow("修饰键:", self.修饰键输入)
        self.输入文本 = QLineEdit()
        表单.addRow("输入文本:", self.输入文本)
        self.按键保持时长 = QSpinBox()
        self.按键保持时长.setRange(100, 60000)
        self.按键保持时长.setSuffix(" ms")
        表单.addRow("保持时长:", self.按键保持时长)
        self.按键延时 = QSpinBox()
        self.按键延时.setRange(0, 60000)
        self.按键延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.按键延时)
        self.堆叠组件.addWidget(页)

    def _创建OCR条件配置页(self) -> None:
        """创建OCR条件判断配置页（合并区域+条件）"""
        页 = QWidget()
        表单 = QFormLayout(页)
        # OCR识别区域配置
        区域布局 = QHBoxLayout()
        self.OCR左上角X = QSpinBox()
        self.OCR左上角X.setRange(0, 9999)
        区域布局.addWidget(QLabel("左上X:"))
        区域布局.addWidget(self.OCR左上角X)
        self.OCR左上角Y = QSpinBox()
        self.OCR左上角Y.setRange(0, 9999)
        区域布局.addWidget(QLabel("左上Y:"))
        区域布局.addWidget(self.OCR左上角Y)
        self.OCR右下角X = QSpinBox()
        self.OCR右下角X.setRange(0, 9999)
        区域布局.addWidget(QLabel("右下X:"))
        区域布局.addWidget(self.OCR右下角X)
        self.OCR右下角Y = QSpinBox()
        self.OCR右下角Y.setRange(0, 9999)
        区域布局.addWidget(QLabel("右下Y:"))
        区域布局.addWidget(self.OCR右下角Y)
        捕获按钮 = QPushButton("框选区域")
        捕获按钮.clicked.connect(lambda: self._启动区域捕获())
        区域布局.addWidget(捕获按钮)
        表单.addRow("识别区域:", 区域布局)
        self.OCR识别语言 = QComboBox()
        self.OCR识别语言.addItems(["中文简体+英文", "中文繁体+英文", "英文", "日文"])
        表单.addRow("识别语言:", self.OCR识别语言)
        # 条件配置
        self.OCR条件类型 = QComboBox()
        self.OCR条件类型.addItems(["文本匹配", "文本不匹配", "文本包含", "文字变化"])
        表单.addRow("条件类型:", self.OCR条件类型)
        self.OCR目标文本 = QLineEdit()
        表单.addRow("目标文本:", self.OCR目标文本)
        self.OCR逻辑关系 = QComboBox()
        self.OCR逻辑关系.addItems(["与", "或"])
        表单.addRow("逻辑关系:", self.OCR逻辑关系)
        self.OCR超时时间 = QSpinBox()
        self.OCR超时时间.setRange(1, 300)
        self.OCR超时时间.setSuffix(" 秒")
        表单.addRow("超时时间:", self.OCR超时时间)
        self.OCR轮询间隔 = QSpinBox()
        self.OCR轮询间隔.setRange(200, 10000)
        self.OCR轮询间隔.setSuffix(" ms")
        表单.addRow("轮询间隔:", self.OCR轮询间隔)
        self.OCR超时处理 = QComboBox()
        self.OCR超时处理.addItems(["跳过继续", "停止脚本", "执行指定步骤"])
        表单.addRow("超时处理:", self.OCR超时处理)
        self.OCR步骤延时 = QSpinBox()
        self.OCR步骤延时.setRange(0, 60000)
        self.OCR步骤延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.OCR步骤延时)
        self.堆叠组件.addWidget(页)

    def _创建延时配置页(self) -> None:
        """创建延时配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        self.延时时长 = QSpinBox()
        self.延时时长.setRange(0, 60000)
        self.延时时长.setSuffix(" ms")
        表单.addRow("延时时长:", self.延时时长)
        self.堆叠组件.addWidget(页)

    def _创建拖拽配置页(self) -> None:
        """创建拖拽配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        起点布局 = QHBoxLayout()
        self.起点X = QSpinBox()
        self.起点X.setRange(0, 9999)
        起点布局.addWidget(self.起点X)
        self.起点Y = QSpinBox()
        self.起点Y.setRange(0, 9999)
        起点布局.addWidget(self.起点Y)
        起点捕获 = QPushButton("捕获起点")
        起点捕获.clicked.connect(lambda: self._启动坐标捕获("起点"))
        起点布局.addWidget(起点捕获)
        表单.addRow("起点X/Y:", 起点布局)
        终点布局 = QHBoxLayout()
        self.终点X = QSpinBox()
        self.终点X.setRange(0, 9999)
        终点布局.addWidget(self.终点X)
        self.终点Y = QSpinBox()
        self.终点Y.setRange(0, 9999)
        终点布局.addWidget(self.终点Y)
        终点捕获 = QPushButton("捕获终点")
        终点捕获.clicked.connect(lambda: self._启动坐标捕获("终点"))
        终点布局.addWidget(终点捕获)
        表单.addRow("终点X/Y:", 终点布局)
        self.拖拽延时 = QSpinBox()
        self.拖拽延时.setRange(0, 60000)
        self.拖拽延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.拖拽延时)
        self.堆叠组件.addWidget(页)

    def _创建调用脚本配置页(self) -> None:
        """创建调用脚本配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        self.调用脚本选择 = QComboBox()
        self._加载可选脚本列表()
        表单.addRow("选择脚本:", self.调用脚本选择)
        提示标签 = QLabel("将执行所选脚本的全部步骤")
        提示标签.setStyleSheet("color: gray; font-size: 11px;")
        表单.addRow("", 提示标签)
        警告标签 = QLabel("注意：不能添加自身或产生循环嵌套")
        警告标签.setStyleSheet("color: #cc6600; font-size: 11px;")
        表单.addRow("", 警告标签)
        self.调用脚本延时 = QSpinBox()
        self.调用脚本延时.setRange(0, 60000)
        self.调用脚本延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.调用脚本延时)
        self.堆叠组件.addWidget(页)

    def _加载可选脚本列表(self) -> None:
        """加载可选脚本列表，排除当前脚本"""
        self.调用脚本选择.clear()
        self.调用脚本选择.addItem("-- 请选择脚本 --", 0)
        if not self.脚本管理服务:
            return
        try:
            脚本列表 = self.脚本管理服务.查询所有脚本()
            for 脚本 in 脚本列表:
                if 脚本.脚本标识 != self.当前脚本标识:
                    self.调用脚本选择.addItem(
                        f"{脚本.脚本名称} ({脚本.步骤数量}步)",
                        脚本.脚本标识
                    )
        except Exception as 异常:
            self.日志.warning(f"加载脚本列表失败: {异常}")

    def _启动坐标捕获(self, 目标: str) -> None:
        """启动坐标捕获模式"""
        self._待捕获目标 = 目标
        self._启动全局鼠标监听()

    def _填充区域坐标(self, 区域: tuple) -> None:
        """填充OCR区域坐标（从上次框选结果）"""
        X1, Y1, X2, Y2 = 区域
        self.OCR左上角X.setValue(X1)
        self.OCR左上角Y.setValue(Y1)
        self.OCR右下角X.setValue(X2)
        self.OCR右下角Y.setValue(Y2)

    def _启动区域捕获(self) -> None:
        """启动OCR区域拖动框选：关闭弹窗，显示全屏覆盖层，选完后重新打开弹窗"""
        from src.表现层.区域框选浮窗 import 区域框选浮窗类

        # 保存当前表单数据
        self._框选前数据 = self.收集步骤数据()

        # 关闭弹窗（结束exec()模态循环）
        self.done(self.区域选择返回码)

        # 最小化主窗口
        if not self._主窗口:
            self._主窗口 = self._查找主窗口()
        if self._主窗口:
            self._主窗口.showMinimized()

        # 显示全屏框选浮窗
        self._区域框选浮窗 = 区域框选浮窗类()
        self._区域框选浮窗.区域已选中.connect(self._区域选中完成信号.emit)
        self._区域框选浮窗.框选已取消.connect(self._处理框选取消)
        self._区域框选浮窗.启动框选()

    def _启动全局鼠标监听(self) -> None:
        """启动pynput全局鼠标监听，最小化主窗口，弹窗移出屏幕"""
        if self.坐标浮窗:
            self.坐标浮窗.停止捕获()
            self.坐标浮窗 = None
        from src.表现层.坐标捕获浮窗 import 坐标捕获浮窗类
        self.坐标浮窗 = 坐标捕获浮窗类()
        self.坐标浮窗.启动捕获()
        if not self._主窗口:
            self._主窗口 = self._查找主窗口()
        if self._主窗口:
            self._主窗口.showMinimized()
        if not self._原位置:
            self._原位置 = self.pos()
        self.move(-32000, -32000)
        try:
            from pynput import mouse
            self._鼠标监听器 = mouse.Listener(on_click=self._全局鼠标点击回调)
            self._鼠标监听器.start()
        except Exception as 异常:
            self.日志.warning(f"全局鼠标监听启动失败: {异常}")
            self._停止捕获()

    def _查找主窗口(self):
        """查找主窗口实例"""
        from PySide6.QtWidgets import QApplication, QMainWindow
        for 窗口 in QApplication.topLevelWidgets():
            if isinstance(窗口, QMainWindow):
                return 窗口
        return None

    def _全局鼠标点击回调(self, x, y, button, pressed) -> None:
        """全局鼠标点击回调（仅用于单点坐标捕获），通过信号通知主线程"""
        if not pressed:
            return
        if button.name == "right":
            self._鼠标监听器.stop()
            self._捕获取消信号.emit()
            return
        if button.name != "left":
            return
        self._鼠标监听器.stop()
        self._坐标捕获完成信号.emit(x, y)

    def _处理全局捕获结果(self, X: int, Y: int) -> None:
        """处理全局捕获的单点坐标结果"""
        if self._待捕获目标 == "鼠标":
            self.鼠标坐标X.setValue(X)
            self.鼠标坐标Y.setValue(Y)
        elif self._待捕获目标 == "起点":
            self.起点X.setValue(X)
            self.起点Y.setValue(Y)
        elif self._待捕获目标 == "终点":
            self.终点X.setValue(X)
            self.终点Y.setValue(Y)
        self._停止捕获()

    def _处理区域选中(self, X1: int, Y1: int, X2: int, Y2: int) -> None:
        """处理区域框选结果，恢复主窗口"""
        self._框选结果区域 = (X1, Y1, X2, Y2)
        self._框选已完成 = True
        self._恢复主窗口()

    def _处理框选取消(self) -> None:
        """处理框选取消，恢复主窗口"""
        self._框选结果区域 = None
        self._框选已完成 = True
        self._恢复主窗口()

    def _恢复主窗口(self) -> None:
        """恢复主窗口（弹窗已通过done()关闭）"""
        self._区域框选浮窗 = None
        if self._主窗口:
            self._主窗口.showNormal()
            self._主窗口.activateWindow()
            self._主窗口 = None

    def _取消捕获(self) -> None:
        """取消坐标捕获"""
        self._停止捕获()

    def _停止捕获(self) -> None:
        """停止捕获模式，恢复窗口"""
        if self._鼠标监听器:
            try:
                self._鼠标监听器.stop()
            except Exception:
                pass
            self._鼠标监听器 = None
        if self.坐标浮窗:
            self.坐标浮窗.停止捕获()
            self.坐标浮窗 = None
        if self._区域框选浮窗:
            self._区域框选浮窗.关闭框选()
            self._区域框选浮窗 = None
        self._待捕获目标 = None
        if self._原位置:
            self.move(self._原位置)
            self._原位置 = None
        if self._主窗口:
            self._主窗口.showNormal()
            self._主窗口.activateWindow()
            self._主窗口 = None
        QTimer.singleShot(100, self._激活弹窗)

    def _激活弹窗(self) -> None:
        """延迟激活弹窗到前台"""
        try:
            import ctypes
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
            ctypes.windll.user32.SetForegroundWindow(int(self.winId()))
        except Exception:
            pass
        self.raise_()
        self.activateWindow()

    def 收集步骤数据(self) -> 操作步骤数据:
        """从界面收集步骤数据"""
        步骤 = 操作步骤数据(操作类型=self.操作类型)
        当前索引 = self.堆叠组件.currentIndex()
        if 当前索引 == 0:
            步骤.目标坐标X = self.鼠标坐标X.value()
            步骤.目标坐标Y = self.鼠标坐标Y.value()
            步骤.步骤延时 = self.鼠标延时.value()
        elif 当前索引 == 1:
            步骤.按键值 = self.按键值输入.text()
            步骤.修饰键列表 = self.修饰键输入.text()
            步骤.输入文本 = self.输入文本.text()
            步骤.按键保持时长 = self.按键保持时长.value()
            步骤.步骤延时 = self.按键延时.value()
        elif 当前索引 == 2:
            # OCR条件判断（合并区域+条件）
            步骤.OCR区域左上角X = self.OCR左上角X.value()
            步骤.OCR区域左上角Y = self.OCR左上角Y.value()
            步骤.OCR区域右下角X = self.OCR右下角X.value()
            步骤.OCR区域右下角Y = self.OCR右下角Y.value()
            步骤.OCR识别语言 = self.OCR识别语言.currentText()
            步骤.OCR条件类型 = self.OCR条件类型.currentText()
            步骤.OCR目标文本 = self.OCR目标文本.text()
            步骤.OCR逻辑关系 = self.OCR逻辑关系.currentText()
            步骤.OCR超时时间 = self.OCR超时时间.value()
            步骤.OCR轮询间隔 = self.OCR轮询间隔.value()
            步骤.OCR超时处理 = self.OCR超时处理.currentText()
            步骤.步骤延时 = self.OCR步骤延时.value()
        elif 当前索引 == 3:
            步骤.延时时长 = self.延时时长.value()
        elif 当前索引 == 4:
            步骤.起点坐标X = self.起点X.value()
            步骤.起点坐标Y = self.起点Y.value()
            步骤.终点坐标X = self.终点X.value()
            步骤.终点坐标Y = self.终点Y.value()
            步骤.步骤延时 = self.拖拽延时.value()
        elif 当前索引 == 5:
            步骤.引用脚本标识 = self.调用脚本选择.currentData() or None
            步骤.步骤延时 = self.调用脚本延时.value()
        return 步骤

    def _加载已有数据(self, 步骤: 操作步骤数据) -> None:
        """加载已有步骤数据"""
        try:
            类型 = 操作类型枚举(步骤.操作类型)
            if 类型 == 操作类型枚举.鼠标拖拽:
                self.起点X.setValue(步骤.起点坐标X or 0)
                self.起点Y.setValue(步骤.起点坐标Y or 0)
                self.终点X.setValue(步骤.终点坐标X or 0)
                self.终点Y.setValue(步骤.终点坐标Y or 0)
                self.拖拽延时.setValue(步骤.步骤延时)
            elif 鼠标操作类型集合.包含(类型):
                self.鼠标坐标X.setValue(步骤.目标坐标X or 0)
                self.鼠标坐标Y.setValue(步骤.目标坐标Y or 0)
                self.鼠标延时.setValue(步骤.步骤延时)
            elif 按键操作类型集合.包含(类型):
                self.按键值输入.setText(步骤.按键值 or "")
                self.修饰键输入.setText(步骤.修饰键列表 or "")
                self.输入文本.setText(步骤.输入文本 or "")
                self.按键保持时长.setValue(步骤.按键保持时长 or 1000)
                self.按键延时.setValue(步骤.步骤延时)
            elif 类型 == 操作类型枚举.OCR条件判断:
                self.OCR左上角X.setValue(步骤.OCR区域左上角X or 0)
                self.OCR左上角Y.setValue(步骤.OCR区域左上角Y or 0)
                self.OCR右下角X.setValue(步骤.OCR区域右下角X or 0)
                self.OCR右下角Y.setValue(步骤.OCR区域右下角Y or 0)
                self.OCR识别语言.setCurrentText(步骤.OCR识别语言 or "中文简体+英文")
                self.OCR条件类型.setCurrentText(步骤.OCR条件类型 or "文本匹配")
                self.OCR目标文本.setText(步骤.OCR目标文本 or "")
                self.OCR逻辑关系.setCurrentText(步骤.OCR逻辑关系 or "与")
                self.OCR超时时间.setValue(步骤.OCR超时时间 or 30)
                self.OCR轮询间隔.setValue(步骤.OCR轮询间隔 or 1000)
                self.OCR超时处理.setCurrentText(步骤.OCR超时处理 or "跳过继续")
                self.OCR步骤延时.setValue(步骤.步骤延时)
            elif 类型 == 操作类型枚举.延时:
                self.延时时长.setValue(步骤.延时时长 or 0)
            elif 类型 == 操作类型枚举.调用脚本:
                if 步骤.引用脚本标识:
                    索引 = self.调用脚本选择.findData(步骤.引用脚本标识)
                    if 索引 >= 0:
                        self.调用脚本选择.setCurrentIndex(索引)
                self.调用脚本延时.setValue(步骤.步骤延时)
        except Exception:
            pass

    def reject(self) -> None:
        """取消时停止捕获"""
        self._停止捕获()
        super().reject()
