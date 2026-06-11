import json
from src.公共.数据结构 import 脚本表数据, 操作步骤数据
from src.公共.异常定义 import 脚本格式错误异常
from src.公共.日志管理 import 获取日志管理器


class JSON序列化器类:
    """脚本数据的JSON导入/导出序列化器"""

    当前版本: str = "1.0"

    def __init__(self):
        self.日志 = 获取日志管理器("JSON序列化器")

    def 导出脚本(self, 脚本数据: 脚本表数据, 步骤列表: list[操作步骤数据]) -> dict:
        """将脚本及步骤数据序列化为JSON结构"""
        步骤字典列表 = []
        for 步骤 in 步骤列表:
            步骤字典 = {
                "排序序号": 步骤.排序序号,
                "操作类型": 步骤.操作类型,
                "步骤延时": 步骤.步骤延时,
            }
            可选字段 = {
                "目标坐标X": 步骤.目标坐标X,
                "目标坐标Y": 步骤.目标坐标Y,
                "按键值": 步骤.按键值,
                "修饰键列表": 步骤.修饰键列表,
                "输入文本": 步骤.输入文本,
                "滚轮量": 步骤.滚轮量,
                "按键保持时长": 步骤.按键保持时长,
                "延时时长": 步骤.延时时长,
                "起点坐标X": 步骤.起点坐标X,
                "起点坐标Y": 步骤.起点坐标Y,
                "终点坐标X": 步骤.终点坐标X,
                "终点坐标Y": 步骤.终点坐标Y,
                "OCR区域左上角X": 步骤.OCR区域左上角X,
                "OCR区域左上角Y": 步骤.OCR区域左上角Y,
                "OCR区域右下角X": 步骤.OCR区域右下角X,
                "OCR区域右下角Y": 步骤.OCR区域右下角Y,
                "OCR识别语言": 步骤.OCR识别语言,
                "OCR条件类型": 步骤.OCR条件类型,
                "OCR目标文本": 步骤.OCR目标文本,
                "OCR逻辑关系": 步骤.OCR逻辑关系,
                "OCR超时时间": 步骤.OCR超时时间,
                "OCR轮询间隔": 步骤.OCR轮询间隔,
                "OCR超时处理": 步骤.OCR超时处理,
                "父步骤标识": 步骤.父步骤标识,
                "分支类型": 步骤.分支类型,
            }
            for 键, 值 in 可选字段.items():
                if 值 is not None:
                    步骤字典[键] = 值
            步骤字典列表.append(步骤字典)

        return {
            "版本": self.当前版本,
            "脚本名称": 脚本数据.脚本名称,
            "脚本描述": 脚本数据.脚本描述,
            "创建时间": 脚本数据.创建时间,
            "修改时间": 脚本数据.修改时间,
            "操作步骤": 步骤字典列表,
        }

    def 导入脚本(self, JSON数据: dict) -> tuple[脚本表数据, list[操作步骤数据]]:
        """从JSON结构反序列化脚本及步骤数据"""
        错误列表 = self.校验格式(JSON数据)
        if 错误列表:
            raise 脚本格式错误异常("; ".join(错误列表))

        脚本数据 = 脚本表数据(
            脚本名称=JSON数据["脚本名称"],
            脚本描述=JSON数据.get("脚本描述", ""),
            创建时间=JSON数据.get("创建时间", ""),
            修改时间=JSON数据.get("修改时间", ""),
        )

        步骤列表 = []
        for 步骤字典 in JSON数据.get("操作步骤", []):
            步骤 = 操作步骤数据(
                排序序号=步骤字典.get("排序序号", 0),
                操作类型=步骤字典.get("操作类型", ""),
                步骤延时=步骤字典.get("步骤延时", 0),
                目标坐标X=步骤字典.get("目标坐标X"),
                目标坐标Y=步骤字典.get("目标坐标Y"),
                按键值=步骤字典.get("按键值"),
                修饰键列表=步骤字典.get("修饰键列表"),
                输入文本=步骤字典.get("输入文本"),
                滚轮量=步骤字典.get("滚轮量"),
                按键保持时长=步骤字典.get("按键保持时长"),
                延时时长=步骤字典.get("延时时长"),
                起点坐标X=步骤字典.get("起点坐标X"),
                起点坐标Y=步骤字典.get("起点坐标Y"),
                终点坐标X=步骤字典.get("终点坐标X"),
                终点坐标Y=步骤字典.get("终点坐标Y"),
                OCR区域左上角X=步骤字典.get("OCR区域左上角X"),
                OCR区域左上角Y=步骤字典.get("OCR区域左上角Y"),
                OCR区域右下角X=步骤字典.get("OCR区域右下角X"),
                OCR区域右下角Y=步骤字典.get("OCR区域右下角Y"),
                OCR识别语言=步骤字典.get("OCR识别语言"),
                OCR条件类型=步骤字典.get("OCR条件类型"),
                OCR目标文本=步骤字典.get("OCR目标文本"),
                OCR逻辑关系=步骤字典.get("OCR逻辑关系"),
                OCR超时时间=步骤字典.get("OCR超时时间"),
                OCR轮询间隔=步骤字典.get("OCR轮询间隔"),
                OCR超时处理=步骤字典.get("OCR超时处理"),
                父步骤标识=步骤字典.get("父步骤标识"),
                分支类型=步骤字典.get("分支类型"),
            )
            步骤列表.append(步骤)

        return 脚本数据, 步骤列表

    def 校验格式(self, JSON数据: dict) -> list[str]:
        """校验JSON数据格式，返回错误列表"""
        错误列表 = []
        if not isinstance(JSON数据, dict):
            错误列表.append("JSON数据必须是字典类型")
            return 错误列表
        if "版本" not in JSON数据:
            错误列表.append("缺少必填字段: 版本")
        if "脚本名称" not in JSON数据:
            错误列表.append("缺少必填字段: 脚本名称")
        elif not JSON数据["脚本名称"]:
            错误列表.append("脚本名称不能为空")
        if "操作步骤" not in JSON数据:
            错误列表.append("缺少必填字段: 操作步骤")
        elif not isinstance(JSON数据["操作步骤"], list):
            错误列表.append("操作步骤必须是数组类型")
        else:
            合法操作类型 = {
                "鼠标移动", "鼠标左键单击", "鼠标左键双击", "鼠标右键单击",
                "鼠标滚轮上滚", "鼠标滚轮下滚", "鼠标拖拽",
                "键盘按键", "键盘组合键", "文本输入", "按键保持",
                "OCR条件判断", "延时",
            }
            for 索引, 步骤 in enumerate(JSON数据["操作步骤"]):
                if not isinstance(步骤, dict):
                    错误列表.append(f"操作步骤[{索引}]必须是字典类型")
                    continue
                if "操作类型" not in 步骤:
                    错误列表.append(f"操作步骤[{索引}]缺少必填字段: 操作类型")
                elif 步骤["操作类型"] not in 合法操作类型:
                    错误列表.append(f"操作步骤[{索引}]操作类型不合法: {步骤['操作类型']}")
        return 错误列表

    def 写入文件(self, 数据: dict, 文件路径: str) -> None:
        """将JSON数据写入文件"""
        with open(文件路径, "w", encoding="utf-8") as 文件:
            json.dump(数据, 文件, ensure_ascii=False, indent=2)

    def 读取文件(self, 文件路径: str) -> dict:
        """从文件读取JSON数据"""
        try:
            with open(文件路径, "r", encoding="utf-8") as 文件:
                return json.load(文件)
        except json.JSONDecodeError as 异常:
            raise 脚本格式错误异常(f"JSON文件格式错误: {异常}", 异常)
        except FileNotFoundError:
            raise 脚本格式错误异常(f"文件不存在: {文件路径}")