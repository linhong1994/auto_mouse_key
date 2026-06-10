from typing import Callable
from PySide6.QtCore import QObject, Signal
from src.公共.数据结构 import 操作步骤数据, 步骤执行结果, 步骤预览信息, 悬浮窗日志条目
from src.公共.枚举定义 import 运行状态枚举
from src.公共.日志管理 import 获取日志管理器


class 执行引擎类(QObject):
    """操作执行引擎，统一管理脚本执行流程"""

    状态变更信号 = Signal(str, str)
    步骤执行信号 = Signal(object)
    日志信号 = Signal(object)

    def __init__(self, 回放控制器=None, 脚本管理服务=None, 步骤管理服务=None):
        super().__init__()
        self.回放控制器 = 回放控制器
        self.脚本管理服务 = 脚本管理服务
        self.步骤管理服务 = 步骤管理服务
        self.当前状态: 运行状态枚举 = 运行状态枚举.空闲
        self._订阅者列表: list[Callable] = []
        self.日志 = 获取日志管理器("执行引擎")
        self._连接信号()

    def 执行脚本(self, 脚本标识: int, 速度倍率: float = 1.0, 循环次数: int = 1) -> None:
        """执行指定脚本"""
        if self.当前状态 != 运行状态枚举.空闲:
            self.日志.warning("当前非空闲状态，无法执行脚本")
            return
        if not self.步骤管理服务 or not self.回放控制器:
            return
        步骤列表 = self.步骤管理服务.查询脚本步骤(脚本标识)
        if not 步骤列表:
            self.日志.warning(f"脚本{脚本标识}无操作步骤")
            return
        self.设置状态(运行状态枚举.回放中)
        预览列表 = [步骤预览信息(步骤序号=s.排序序号, 操作类型=s.操作类型, 参数摘要=self._生成参数摘要(s)) for s in 步骤列表]
        self.步骤执行信号.emit(预览列表)
        self.回放控制器.启动回放(步骤列表, 速度倍率, 循环次数)

    def 停止执行(self) -> None:
        """紧急停止当前执行"""
        if self.回放控制器:
            self.回放控制器.紧急停止()
        self.设置状态(运行状态枚举.空闲)

    def 订阅状态变更(self, 回调函数: Callable) -> None:
        """订阅执行状态变更通知"""
        self._订阅者列表.append(回调函数)

    def 取消订阅(self, 回调函数: Callable) -> None:
        """取消状态变更订阅"""
        if 回调函数 in self._订阅者列表:
            self._订阅者列表.remove(回调函数)

    def 设置状态(self, 新状态: 运行状态枚举, 进度: str = "") -> None:
        """设置当前运行状态并通知订阅者"""
        旧状态 = self.当前状态
        self.当前状态 = 新状态
        self.状态变更信号.emit(新状态.value, 进度)
        for 回调 in self._订阅者列表:
            try:
                回调(新状态, 进度)
            except Exception:
                pass

    def _连接信号(self) -> None:
        """连接回放控制器的信号"""
        if self.回放控制器:
            self.回放控制器.步骤执行完成.connect(self._处理步骤执行结果)
            self.回放控制器.回放完成.connect(self._处理回放完成)

    def _处理步骤执行结果(self, 结果: 步骤执行结果) -> None:
        """处理步骤执行结果"""
        from datetime import datetime
        日志条目 = 悬浮窗日志条目(
            日志时间戳=datetime.now().strftime("%H:%M:%S"),
            操作描述=f"步骤{结果.步骤序号}",
            执行结果="成功" if 结果.执行成功 else "失败",
            附加信息=结果.错误信息 or "",
        )
        self.日志信号.emit(日志条目)

    def _处理回放完成(self, 成功: bool) -> None:
        """处理回放完成"""
        self.设置状态(运行状态枚举.空闲 if 成功 else 运行状态枚举.执行失败)

    def _生成参数摘要(self, 步骤: 操作步骤数据) -> str:
        """生成步骤参数摘要文本"""
        from src.公共.枚举定义 import 操作类型枚举, 鼠标操作类型集合, 按键操作类型集合
        try:
            操作类型 = 操作类型枚举(步骤.操作类型)
            if 鼠标操作类型集合.包含(操作类型):
                return f"({步骤.目标坐标X}, {步骤.目标坐标Y})"
            elif 按键操作类型集合.包含(操作类型):
                return 步骤.按键值 or 步骤.输入文本 or ""
            elif 操作类型 == 操作类型枚举.延时:
                return f"{步骤.延时时长}ms"
            elif 操作类型 in (操作类型枚举.OCR识别, 操作类型枚举.OCR条件判断):
                return f"({步骤.OCR区域左上角X},{步骤.OCR区域左上角Y})-({步骤.OCR区域右下角X},{步骤.OCR区域右下角Y})"
        except Exception:
            pass
        return ""