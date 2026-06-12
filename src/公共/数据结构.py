from dataclasses import dataclass, field
from src.公共.枚举定义 import 操作类型枚举, 运行状态枚举, OCR条件类型枚举, OCR超时处理枚举, 定时触发类型枚举


@dataclass
class 操作步骤数据:
    """操作步骤数据结构，对应操作步骤表的一条记录"""
    步骤标识: int = 0
    所属脚本标识: int = 0
    操作类型: str = ""
    步骤名称: str | None = None
    排序序号: int = 0
    目标坐标X: int | None = None
    目标坐标Y: int | None = None
    按键值: str | None = None
    修饰键列表: str | None = None
    输入文本: str | None = None
    步骤延时: int = 0
    滚轮量: int | None = None
    按键保持时长: int | None = None
    延时时长: int | None = None
    起点坐标X: int | None = None
    起点坐标Y: int | None = None
    终点坐标X: int | None = None
    终点坐标Y: int | None = None
    OCR区域左上角X: int | None = None
    OCR区域左上角Y: int | None = None
    OCR区域右下角X: int | None = None
    OCR区域右下角Y: int | None = None
    OCR识别语言: str | None = None
    OCR条件类型: str | None = None
    OCR目标文本: str | None = None
    OCR逻辑关系: str | None = None
    OCR超时时间: int | None = None
    OCR轮询间隔: int | None = None
    OCR超时处理: str | None = None
    父步骤标识: int | None = None
    分支类型: str | None = None
    引用脚本标识: int | None = None


@dataclass
class 脚本概要信息:
    """脚本概要信息，用于脚本列表展示"""
    脚本标识: int
    脚本名称: str
    步骤数量: int
    创建时间: str
    修改时间: str
    脚本描述: str = ""


@dataclass
class 脚本表数据:
    """脚本表完整数据，对应脚本表的一条记录"""
    脚本标识: int = 0
    脚本名称: str = ""
    脚本描述: str = ""
    创建时间: str = ""
    修改时间: str = ""
    定时触发类型: str | None = None
    定时触发时间: str | None = None
    定时循环间隔: int | None = None
    定时每日时间: str | None = None
    定时启用: bool = False


@dataclass

class 热键配置数据:
    """热键配置数据结构，对应热键配置表的一条记录"""
    配置标识: int = 0
    功能名称: str = ""
    热键组合: str = ""
    全局生效: bool = True


@dataclass
class 文字行信息:
    """单行文字识别信息"""
    行文本: str = ""
    行坐标X: int = 0
    行坐标Y: int = 0
    行宽度: int = 0
    行高度: int = 0
    行置信度: float = 0.0


@dataclass
class OCR识别结果:
    """OCR识别结果数据结构"""
    识别文本: str = ""
    文字行列表: list[文字行信息] = field(default_factory=list)
    识别耗时: int = 0
    识别时间戳: str = ""
    平均置信度: float = 0.0
    低可信度: bool = False


@dataclass
class OCR触发条件:
    """OCR触发条件数据结构"""
    条件类型: str = "文本匹配"
    识别区域: tuple[int, int, int, int] = (0, 0, 0, 0)
    目标文本: str = ""
    识别语言: str = "中文简体+英文"
    超时时间: int = 10
    轮询间隔: int = 500
    超时处理: str = "跳过继续"


@dataclass
class OCR识别记录:
    """OCR识别历史记录"""
    记录标识: int = 0
    识别时间戳: str = ""
    识别区域: tuple[int, int, int, int] = (0, 0, 0, 0)
    识别语言: str = ""
    识别文本: str = ""
    平均置信度: float = 0.0


@dataclass
class 步骤执行结果:
    """步骤执行结果"""
    步骤序号: int = 0
    执行成功: bool = True
    执行耗时: int = 0
    错误信息: str | None = None


@dataclass
class 悬浮窗日志条目:
    """悬浮窗运行日志条目"""
    日志时间戳: str = ""
    操作描述: str = ""
    执行结果: str = "成功"
    附加信息: str = ""


@dataclass
class 步骤预览信息:
    """即将运行的操作步骤预览"""
    步骤序号: int = 0
    操作类型: str = ""
    参数摘要: str = ""