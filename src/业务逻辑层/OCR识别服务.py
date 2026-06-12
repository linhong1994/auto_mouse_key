import time
import os
from datetime import datetime
from PIL import ImageGrab
from src.公共.数据结构 import OCR识别结果, 文字行信息, OCR识别记录
from src.公共.异常定义 import OCR引擎异常
from src.公共.日志管理 import 获取日志管理器


class OCR识别服务类:
    """OCR文字识别服务，基于RapidOCR引擎，负责屏幕区域截图与文字识别"""

    def __init__(self, 配置DAO=None):
        self.配置DAO = 配置DAO
        self.引擎 = None
        self.引擎可用 = False
        self.历史记录: list[OCR识别记录] = []
        self.日志 = 获取日志管理器("OCR识别服务")
        self._初始化引擎()

    def _初始化引擎(self) -> None:
        """初始化RapidOCR引擎"""
        try:
            from rapidocr import RapidOCR
            self.引擎 = RapidOCR()
            self.引擎可用 = True
            self.日志.info("OCR引擎初始化成功（RapidOCR）")
        except Exception as 异常:
            self.引擎可用 = False
            self.日志.warning(f"OCR引擎初始化失败，OCR功能不可用: {异常}")

    def 识别区域(self, 左上角X: int, 左上角Y: int, 右下角X: int, 右下角Y: int,
                 识别语言: str = "中文简体+英文", 精度: str = "标准精度") -> OCR识别结果:
        """对指定屏幕区域执行OCR文字识别"""
        if not self.引擎可用:
            raise OCR引擎异常("OCR引擎不可用，请检查RapidOCR安装")
        区域坐标 = self._校验识别区域((左上角X, 左上角Y, 右下角X, 右下角Y))
        开始时间 = time.perf_counter()
        try:
            图像 = self._截取屏幕区域(区域坐标)
            结果 = self._调用引擎识别(图像, 识别语言)
            耗时 = int((time.perf_counter() - 开始时间) * 1000)
            结果.识别耗时 = 耗时
            结果.识别时间戳 = datetime.now().isoformat()
            self._记录历史(区域坐标, 识别语言, 结果)
            return 结果
        except OCR引擎异常:
            raise
        except Exception as 异常:
            self.日志.error(f"OCR识别失败: {异常}")
            raise OCR引擎异常(f"OCR识别失败: {异常}", 异常)

    def 识别全屏(self, 识别语言: str = "中文简体+英文") -> OCR识别结果:
        """对当前全屏执行OCR文字识别"""
        屏幕宽度, 屏幕高度 = ImageGrab.grab().size
        return self.识别区域(0, 0, 屏幕宽度, 屏幕高度, 识别语言)

    def 复制结果到剪贴板(self, 识别结果: OCR识别结果) -> None:
        """将识别文本复制到系统剪贴板"""
        try:
            import pyperclip
            pyperclip.copy(识别结果.识别文本)
        except Exception as 异常:
            self.日志.error(f"复制到剪贴板失败: {异常}")

    def 导出结果为文件(self, 识别结果: OCR识别结果, 文件路径: str) -> None:
        """将识别结果导出为文本文件"""
        try:
            with open(文件路径, "w", encoding="utf-8") as 文件:
                文件.write(识别结果.识别文本)
        except Exception as 异常:
            self.日志.error(f"导出结果失败: {异常}")

    def 获取历史记录(self, 条数: int = 20) -> list[OCR识别记录]:
        """获取最近的OCR识别历史记录"""
        return self.历史记录[-条数:]

    def _截取屏幕区域(self, 区域坐标: tuple[int, int, int, int]):
        """截取指定屏幕区域的图像"""
        左上角X, 左上角Y, 右下角X, 右下角Y = 区域坐标
        return ImageGrab.grab(bbox=(左上角X, 左上角Y, 右下角X, 右下角Y))

    def _调用引擎识别(self, 图像, 语言配置: str) -> OCR识别结果:
        """调用RapidOCR引擎执行识别"""
        if not self.引擎可用:
            raise OCR引擎异常("OCR引擎不可用")
        try:
            引擎结果, _ = self.引擎(图像)
            文字行列表 = []
            全部文本 = []
            置信度总和 = 0.0
            行数 = 0
            if 引擎结果:
                for 行数据 in 引擎结果:
                    坐标, 文本, 置信度 = 行数据
                    全部文本.append(文本)
                    置信度总和 += 置信度
                    行数 += 1
                    左上角 = 坐标[0]
                    右下角 = 坐标[2]
                    文字行列表.append(文字行信息(
                        行文本=文本,
                        行坐标X=int(左上角[0]),
                        行坐标Y=int(左上角[1]),
                        行宽度=int(右下角[0] - 左上角[0]),
                        行高度=int(右下角[1] - 左上角[1]),
                        行置信度=置信度,
                    ))
            平均置信度 = 置信度总和 / 行数 if 行数 > 0 else 0.0
            置信度阈值 = 30
            if self.配置DAO:
                try:
                    置信度阈值 = int(self.配置DAO.查询配置("OCR置信度阈值", "30"))
                except Exception:
                    pass
            return OCR识别结果(
                识别文本="\n".join(全部文本),
                文字行列表=文字行列表,
                平均置信度=平均置信度,
                低可信度=平均置信度 < 置信度阈值 / 100.0,
            )
        except Exception as 异常:
            self.引擎可用 = False
            raise OCR引擎异常(f"OCR引擎调用失败: {异常}", 异常)

    def _校验识别区域(self, 区域坐标: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        """校验并裁剪识别区域到屏幕有效范围"""
        左上角X, 左上角Y, 右下角X, 右下角Y = 区域坐标
        屏幕宽度, 屏幕高度 = ImageGrab.grab().size
        左上角X = max(0, min(左上角X, 屏幕宽度))
        左上角Y = max(0, min(左上角Y, 屏幕高度))
        右下角X = max(左上角X, min(右下角X, 屏幕宽度))
        右下角Y = max(左上角Y, min(右下角Y, 屏幕高度))
        return (左上角X, 左上角Y, 右下角X, 右下角Y)

    def _记录历史(self, 区域坐标: tuple, 识别语言: str, 结果: OCR识别结果) -> None:
        """记录识别历史"""
        记录 = OCR识别记录(
            识别时间戳=结果.识别时间戳,
            识别区域=区域坐标,
            识别语言=识别语言,
            识别文本=结果.识别文本,
            平均置信度=结果.平均置信度,
        )
        self.历史记录.append(记录)
        if len(self.历史记录) > 100:
            self.历史记录 = self.历史记录[-100:]
