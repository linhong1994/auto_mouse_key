from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QScrollArea, QGroupBox,
)
from PySide6.QtCore import Qt
from src.公共.数据结构 import 操作步骤数据
from src.公共.枚举定义 import 操作类型枚举, 鼠标操作类型集合, 按键操作类型集合
from src.公共.日志管理 import 获取日志管理器


class 步骤详情组件类(QWidget):
    """步骤详情只读面板，根据操作类型动态显示相关字段"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.日志 = 获取日志管理器("步骤详情组件")
        self.初始化界面()

    def 初始化界面(self) -> None:
        """初始化界面"""
        主布局 = QVBoxLayout(self)
        主布局.setContentsMargins(4, 4, 4, 4)

        self.标题标签 = QLabel("步骤详情")
        self.标题标签.setStyleSheet("font-weight: bold; font-size: 13px;")
        主布局.addWidget(self.标题标签)

        # 滚动区域
        self.滚动区域 = QScrollArea()
        self.滚动区域.setWidgetResizable(True)
        self.滚动区域.setFrameShape(QScrollArea.Shape.NoFrame)

        self.表单容器 = QWidget()
        self.表单布局 = QFormLayout(self.表单容器)
        self.表单布局.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.表单布局.setContentsMargins(0, 0, 0, 0)

        self._创建所有字段()
        self.滚动区域.setWidget(self.表单容器)
        主布局.addWidget(self.滚动区域, 1)

        # 初始状态清空
        self.清空详情()

    def _创建所有字段(self) -> None:
        """预创建所有详情字段标签"""
        self.字段 = {}

        # 基础信息
        self._添加字段组("基础信息")
        self._添加字段("步骤标识", "步骤标识")
        self._添加字段("排序序号", "排序序号")
        self._添加字段("操作类型", "操作类型")
        self._添加字段("步骤延时", "步骤延时")

        # 鼠标相关
        self._添加字段组("鼠标参数")
        self._添加字段("目标坐标X", "目标坐标X")
        self._添加字段("目标坐标Y", "目标坐标Y")
        self._添加字段("起点坐标X", "起点坐标X")
        self._添加字段("起点坐标Y", "起点坐标Y")
        self._添加字段("终点坐标X", "终点坐标X")
        self._添加字段("终点坐标Y", "终点坐标Y")
        self._添加字段("滚轮量", "滚轮量")

        # 按键相关
        self._添加字段组("按键参数")
        self._添加字段("按键值", "按键值")
        self._添加字段("修饰键列表", "修饰键列表")
        self._添加字段("输入文本", "输入文本")
        self._添加字段("按键保持时长", "按键保持时长")

        # 延时相关
        self._添加字段组("延时参数")
        self._添加字段("延时时长", "延时时长")

        # OCR相关
        self._添加字段组("OCR参数")
        self._添加字段("OCR区域左上角X", "OCR左上X")
        self._添加字段("OCR区域左上角Y", "OCR左上Y")
        self._添加字段("OCR区域右下角X", "OCR右下X")
        self._添加字段("OCR区域右下角Y", "OCR右下Y")
        self._添加字段("OCR识别语言", "识别语言")
        self._添加字段("OCR结果变量名", "结果变量名")
        self._添加字段("OCR条件类型", "条件类型")
        self._添加字段("OCR目标文本", "目标文本")
        self._添加字段("OCR逻辑关系", "逻辑关系")
        self._添加字段("OCR超时时间", "超时时间")
        self._添加字段("OCR轮询间隔", "轮询间隔")
        self._添加字段("OCR超时处理", "超时处理")

    def _添加字段组(self, 组名: str) -> None:
        """添加分组标题"""
        标签 = QLabel(组名)
        标签.setStyleSheet("font-weight: bold; color: #555; margin-top: 6px;")
        self.表单布局.addRow(标签)

    def _添加字段(self, 字段名: str, 显示名: str) -> None:
        """添加一个只读字段"""
        值标签 = QLabel("-")
        值标签.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        值标签.setWordWrap(True)
        self.字段[字段名] = {
            "标签": 值标签,
            "行标签": QLabel(f"{显示名}:"),
        }
        self.表单布局.addRow(self.字段[字段名]["行标签"], 值标签)

    def 显示步骤详情(self, 步骤: 操作步骤数据) -> None:
        """显示指定步骤的详情"""
        self.标题标签.setText(f"步骤详情 - #{步骤.排序序号} {步骤.操作类型}")

        # 填充所有字段值
        self._设置字段值("步骤标识", str(步骤.步骤标识))
        self._设置字段值("排序序号", str(步骤.排序序号))
        self._设置字段值("操作类型", 步骤.操作类型)
        self._设置字段值("步骤延时", f"{步骤.步骤延时} ms")

        self._设置字段值("目标坐标X", 步骤.目标坐标X)
        self._设置字段值("目标坐标Y", 步骤.目标坐标Y)
        self._设置字段值("起点坐标X", 步骤.起点坐标X)
        self._设置字段值("起点坐标Y", 步骤.起点坐标Y)
        self._设置字段值("终点坐标X", 步骤.终点坐标X)
        self._设置字段值("终点坐标Y", 步骤.终点坐标Y)
        self._设置字段值("滚轮量", 步骤.滚轮量)

        self._设置字段值("按键值", 步骤.按键值)
        self._设置字段值("修饰键列表", 步骤.修饰键列表)
        self._设置字段值("输入文本", 步骤.输入文本)
        self._设置字段值("按键保持时长", 步骤.按键保持时长, 后缀=" ms")

        self._设置字段值("延时时长", 步骤.延时时长, 后缀=" ms")

        self._设置字段值("OCR区域左上角X", 步骤.OCR区域左上角X)
        self._设置字段值("OCR区域左上角Y", 步骤.OCR区域左上角Y)
        self._设置字段值("OCR区域右下角X", 步骤.OCR区域右下角X)
        self._设置字段值("OCR区域右下角Y", 步骤.OCR区域右下角Y)
        self._设置字段值("OCR识别语言", 步骤.OCR识别语言)
        self._设置字段值("OCR结果变量名", 步骤.OCR结果变量名)
        self._设置字段值("OCR条件类型", 步骤.OCR条件类型)
        self._设置字段值("OCR目标文本", 步骤.OCR目标文本)
        self._设置字段值("OCR逻辑关系", 步骤.OCR逻辑关系)
        self._设置字段值("OCR超时时间", 步骤.OCR超时时间, 后缀=" s")
        self._设置字段值("OCR轮询间隔", 步骤.OCR轮询间隔, 后缀=" ms")
        self._设置字段值("OCR超时处理", 步骤.OCR超时处理)

        # 根据操作类型控制字段可见性
        self._更新字段可见性(步骤.操作类型)

    def _设置字段值(self, 字段名: str, 值, 后缀: str = "") -> None:
        """设置字段显示值"""
        if 字段名 not in self.字段:
            return
        if 值 is None or 值 == "" or 值 == 0:
            self.字段[字段名]["标签"].setText("-")
        else:
            self.字段[字段名]["标签"].setText(f"{值}{后缀}")

    def _更新字段可见性(self, 操作类型: str) -> None:
        """根据操作类型显示/隐藏相关字段"""
        try:
            类型枚举 = 操作类型枚举(操作类型)
        except (ValueError, KeyError):
            return

        是鼠标 = 鼠标操作类型集合.包含(类型枚举)
        是按键 = 按键操作类型集合.包含(类型枚举)
        是延时 = (类型枚举 == 操作类型枚举.延时)
        是OCR = (类型枚举 in (操作类型枚举.OCR识别, 操作类型枚举.OCR条件判断))

        # 鼠标字段
        鼠标字段 = ["目标坐标X", "目标坐标Y", "起点坐标X", "起点坐标Y",
                   "终点坐标X", "终点坐标Y", "滚轮量"]
        # 按键字段
        按键字段 = ["按键值", "修饰键列表", "输入文本", "按键保持时长"]
        # 延时字段
        延时字段 = ["延时时长"]
        # OCR字段
        OCR字段 = ["OCR区域左上角X", "OCR区域左上角Y", "OCR区域右下角X", "OCR区域右下角Y",
                   "OCR识别语言", "OCR结果变量名", "OCR条件类型", "OCR目标文本",
                   "OCR逻辑关系", "OCR超时时间", "OCR轮询间隔", "OCR超时处理"]

        self._设置字段组可见(鼠标字段, 是鼠标)
        self._设置字段组可见(按键字段, 是按键)
        self._设置字段组可见(延时字段, 是延时)
        self._设置字段组可见(OCR字段, 是OCR)

    def _设置字段组可见(self, 字段名列表: list[str], 可见: bool) -> None:
        """批量设置字段可见性"""
        for 字段名 in 字段名列表:
            if 字段名 in self.字段:
                self.字段[字段名]["标签"].setVisible(可见)
                self.字段[字段名]["行标签"].setVisible(可见)

    def 清空详情(self) -> None:
        """清空所有详情显示"""
        self.标题标签.setText("步骤详情")
        for 字段名, 字段信息 in self.字段.items():
            字段信息["标签"].setText("-")
        # 隐藏所有条件字段
        全部条件字段 = (
            ["目标坐标X", "目标坐标Y", "起点坐标X", "起点坐标Y",
             "终点坐标X", "终点坐标Y", "滚轮量"]
            + ["按键值", "修饰键列表", "输入文本", "按键保持时长"]
            + ["延时时长"]
            + ["OCR区域左上角X", "OCR区域左上角Y", "OCR区域右下角X", "OCR区域右下角Y",
               "OCR识别语言", "OCR结果变量名", "OCR条件类型", "OCR目标文本",
               "OCR逻辑关系", "OCR超时时间", "OCR轮询间隔", "OCR超时处理"]
        )
        self._设置字段组可见(全部条件字段, False)
