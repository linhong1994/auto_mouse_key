from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QSpinBox,
    QLineEdit, QComboBox, QPushButton, QGroupBox, QStackedWidget,
)
from PySide6.QtCore import Signal
from src.公共.数据结构 import 操作步骤数据
from src.公共.枚举定义 import 操作类型枚举
from src.公共.日志管理 import 获取日志管理器


class 操作配置组件类(QWidget):
    """操作配置区组件，根据操作类型动态显示参数输入界面"""

    步骤保存信号 = Signal(object)

    def __init__(self, 步骤管理服务=None, parent=None):
        super().__init__(parent)
        self.步骤管理服务 = 步骤管理服务
        self.当前步骤标识 = 0
        self.当前脚本标识 = 0
        self.日志 = 获取日志管理器("操作配置组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        布局 = QVBoxLayout(self)
        self.堆叠组件 = QStackedWidget()
        self._创建鼠标配置页()
        self._创建按键配置页()
        self._创建OCR识别配置页()
        self._创建OCR条件配置页()
        self._创建延时配置页()
        self._创建拖拽配置页()
        布局.addWidget(self.堆叠组件)
        保存按钮 = QPushButton("保存步骤")
        保存按钮.clicked.connect(self._保存步骤)
        布局.addWidget(保存按钮)

    def _创建鼠标配置页(self) -> None:
        """创建鼠标操作配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        self.鼠标坐标X = QSpinBox()
        self.鼠标坐标X.setRange(0, 9999)
        表单.addRow("坐标X:", self.鼠标坐标X)
        self.鼠标坐标Y = QSpinBox()
        self.鼠标坐标Y.setRange(0, 9999)
        表单.addRow("坐标Y:", self.鼠标坐标Y)
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

    def _创建OCR识别配置页(self) -> None:
        """创建OCR识别配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
        self.OCR左上角X = QSpinBox()
        self.OCR左上角X.setRange(0, 9999)
        表单.addRow("区域左上X:", self.OCR左上角X)
        self.OCR左上角Y = QSpinBox()
        self.OCR左上角Y.setRange(0, 9999)
        表单.addRow("区域左上Y:", self.OCR左上角Y)
        self.OCR右下角X = QSpinBox()
        self.OCR右下角X.setRange(0, 9999)
        表单.addRow("区域右下X:", self.OCR右下角X)
        self.OCR右下角Y = QSpinBox()
        self.OCR右下角Y.setRange(0, 9999)
        表单.addRow("区域右下Y:", self.OCR右下角Y)
        self.OCR识别语言 = QComboBox()
        self.OCR识别语言.addItems(["中文简体+英文", "中文繁体+英文", "英文", "日文"])
        表单.addRow("识别语言:", self.OCR识别语言)
        self.OCR结果变量名 = QLineEdit()
        表单.addRow("结果变量名:", self.OCR结果变量名)
        self.OCR步骤延时 = QSpinBox()
        self.OCR步骤延时.setRange(0, 60000)
        self.OCR步骤延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.OCR步骤延时)
        self.堆叠组件.addWidget(页)

    def _创建OCR条件配置页(self) -> None:
        """创建OCR条件判断配置页"""
        页 = QWidget()
        表单 = QFormLayout(页)
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
        self.起点X = QSpinBox()
        self.起点X.setRange(0, 9999)
        表单.addRow("起点X:", self.起点X)
        self.起点Y = QSpinBox()
        self.起点Y.setRange(0, 9999)
        表单.addRow("起点Y:", self.起点Y)
        self.终点X = QSpinBox()
        self.终点X.setRange(0, 9999)
        表单.addRow("终点X:", self.终点X)
        self.终点Y = QSpinBox()
        self.终点Y.setRange(0, 9999)
        表单.addRow("终点Y:", self.终点Y)
        self.拖拽延时 = QSpinBox()
        self.拖拽延时.setRange(0, 60000)
        self.拖拽延时.setSuffix(" ms")
        表单.addRow("步骤延时:", self.拖拽延时)
        self.堆叠组件.addWidget(页)

    def 切换配置页(self, 操作类型: str) -> None:
        """根据操作类型切换配置页"""
        from src.公共.枚举定义 import 鼠标操作类型集合, 按键操作类型集合
        try:
            类型 = 操作类型枚举(操作类型)
            if 类型 == 操作类型枚举.鼠标拖拽:
                self.堆叠组件.setCurrentIndex(5)
            elif 鼠标操作类型集合.包含(类型):
                self.堆叠组件.setCurrentIndex(0)
            elif 按键操作类型集合.包含(类型):
                self.堆叠组件.setCurrentIndex(1)
            elif 类型 == 操作类型枚举.OCR识别:
                self.堆叠组件.setCurrentIndex(2)
            elif 类型 == 操作类型枚举.OCR条件判断:
                self.堆叠组件.setCurrentIndex(3)
            elif 类型 == 操作类型枚举.延时:
                self.堆叠组件.setCurrentIndex(4)
        except Exception:
            self.堆叠组件.setCurrentIndex(4)

    def 加载步骤数据(self, 步骤: 操作步骤数据) -> None:
        """加载步骤数据到配置界面"""
        self.当前步骤标识 = 步骤.步骤标识
        self.切换配置页(步骤.操作类型)
        try:
            类型 = 操作类型枚举(步骤.操作类型)
            from src.公共.枚举定义 import 鼠标操作类型集合, 按键操作类型集合
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
            elif 类型 == 操作类型枚举.OCR识别:
                self.OCR左上角X.setValue(步骤.OCR区域左上角X or 0)
                self.OCR左上角Y.setValue(步骤.OCR区域左上角Y or 0)
                self.OCR右下角X.setValue(步骤.OCR区域右下角X or 0)
                self.OCR右下角Y.setValue(步骤.OCR区域右下角Y or 0)
                self.OCR步骤延时.setValue(步骤.步骤延时)
            elif 类型 == 操作类型枚举.延时:
                self.延时时长.setValue(步骤.延时时长 or 0)
        except Exception:
            pass

    def _保存步骤(self) -> None:
        """保存步骤配置"""
        self.步骤保存信号.emit(self.收集步骤数据())

    def 收集步骤数据(self) -> 操作步骤数据:
        """从界面收集步骤数据"""
        当前索引 = self.堆叠组件.currentIndex()
        步骤 = 操作步骤数据(步骤标识=self.当前步骤标识, 所属脚本标识=self.当前脚本标识)
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
            步骤.OCR区域左上角X = self.OCR左上角X.value()
            步骤.OCR区域左上角Y = self.OCR左上角Y.value()
            步骤.OCR区域右下角X = self.OCR右下角X.value()
            步骤.OCR区域右下角Y = self.OCR右下角Y.value()
            步骤.OCR识别语言 = self.OCR识别语言.currentText()
            步骤.OCR结果变量名 = self.OCR结果变量名.text()
            步骤.步骤延时 = self.OCR步骤延时.value()
        elif 当前索引 == 3:
            步骤.OCR条件类型 = self.OCR条件类型.currentText()
            步骤.OCR目标文本 = self.OCR目标文本.text()
            步骤.OCR逻辑关系 = self.OCR逻辑关系.currentText()
            步骤.OCR超时时间 = self.OCR超时时间.value()
            步骤.OCR轮询间隔 = self.OCR轮询间隔.value()
            步骤.OCR超时处理 = self.OCR超时处理.currentText()
        elif 当前索引 == 4:
            步骤.延时时长 = self.延时时长.value()
        elif 当前索引 == 5:
            步骤.起点坐标X = self.起点X.value()
            步骤.起点坐标Y = self.起点Y.value()
            步骤.终点坐标X = self.终点X.value()
            步骤.终点坐标Y = self.终点Y.value()
            步骤.步骤延时 = self.拖拽延时.value()
        return 步骤