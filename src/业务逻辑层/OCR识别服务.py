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
            self._保存识别区域图片(图像)
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
        """截取指定屏幕区域的图像，返回numpy数组，自动处理DPI缩放"""
        左上角X, 左上角Y, 右下角X, 右下角Y = 区域坐标
        缩放比 = self._获取DPI缩放比()
        物理坐标 = (int(左上角X * 缩放比), int(左上角Y * 缩放比),
                    int(右下角X * 缩放比), int(右下角Y * 缩放比))
        图像 = ImageGrab.grab(bbox=物理坐标)
        import numpy as np
        return np.array(图像)

    def _获取DPI缩放比(self) -> float:
        """获取系统DPI缩放比例"""
        try:
            import ctypes
            桌面DC = ctypes.windll.user32.GetDC(0)
            水平DPI = ctypes.windll.gdi32.GetDeviceCaps(桌面DC, 88)
            ctypes.windll.user32.ReleaseDC(0, 桌面DC)
            return 水平DPI / 96.0
        except Exception:
            return 1.0

    def _保存识别区域图片(self, 图像) -> None:
        """保存OCR识别区域截图到日志目录，用于分析识别失败原因"""
        try:
            from pathlib import Path
            日志目录 = Path("logs/ocr_screenshots")
            日志目录.mkdir(parents=True, exist_ok=True)
            时间戳 = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            文件路径 = 日志目录 / f"ocr_{时间戳}.png"
            import cv2
            cv2.imwrite(str(文件路径), cv2.cvtColor(图像, cv2.COLOR_RGB2BGR))
            self.日志.info(f"OCR识别区域截图已保存: {文件路径}")
        except Exception as 异常:
            self.日志.warning(f"保存OCR识别区域截图失败: {异常}")

    def _调用引擎识别(self, 图像, 语言配置: str) -> OCR识别结果:
        """调用RapidOCR引擎执行识别"""
        if not self.引擎可用:
            raise OCR引擎异常("OCR引擎不可用")
        try:
            引擎输出 = self.引擎(图像)

            if hasattr(引擎输出, 'txts'):
                return self._解析新版本输出(引擎输出)
            elif isinstance(引擎输出, tuple):
                return self._解析旧版本输出(引擎输出)
            else:
                raise OCR引擎异常(f"未知的OCR输出类型: {type(引擎输出)}")
        except OCR引擎异常:
            raise
        except Exception as 异常:
            self.引擎可用 = False
            raise OCR引擎异常(f"OCR引擎调用失败: {异常}", 异常)

    def _解析新版本输出(self, 输出) -> OCR识别结果:
        """解析RapidOCR 3.x的RapidOCROutput对象"""
        文字行列表 = []
        全部文本 = []
        置信度总和 = 0.0
        行数 = 0
        if 输出.txts is not None and 输出.boxes is not None and 输出.scores is not None:
            for i, (文本, 置信度) in enumerate(zip(输出.txts, 输出.scores)):
                全部文本.append(文本)
                置信度总和 += 置信度
                行数 += 1
                坐标 = 输出.boxes[i]
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
        置信度阈值 = self._获取置信度阈值()
        return OCR识别结果(
            识别文本="\n".join(全部文本),
            文字行列表=文字行列表,
            平均置信度=平均置信度,
            低可信度=平均置信度 < 置信度阈值 / 100.0,
        )

    def _解析旧版本输出(self, 输出) -> OCR识别结果:
        """解析RapidOCR 1.x/2.x的(result, elapsed)元组输出"""
        引擎结果, _ = 输出
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
        置信度阈值 = self._获取置信度阈值()
        return OCR识别结果(
            识别文本="\n".join(全部文本),
            文字行列表=文字行列表,
            平均置信度=平均置信度,
            低可信度=平均置信度 < 置信度阈值 / 100.0,
        )

    def _获取置信度阈值(self) -> int:
        """获取OCR置信度阈值配置"""
        置信度阈值 = 30
        if self.配置DAO:
            try:
                置信度阈值 = int(self.配置DAO.查询配置("OCR置信度阈值", "30"))
            except Exception:
                pass
        return 置信度阈值

    def _校验识别区域(self, 区域坐标: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        """校验并裁剪识别区域到屏幕有效范围"""
        左上角X, 左上角Y, 右下角X, 右下角Y = 区域坐标
        屏幕宽度, 屏幕高度 = ImageGrab.grab().size
        缩放比 = self._获取DPI缩放比()
        物理宽度 = 屏幕宽度
        物理高度 = 屏幕高度
        逻辑宽度 = int(物理宽度 / 缩放比)
        逻辑高度 = int(物理高度 / 缩放比)
        左上角X = max(0, min(左上角X, 逻辑宽度))
        左上角Y = max(0, min(左上角Y, 逻辑高度))
        右下角X = max(左上角X, min(右下角X, 逻辑宽度))
        右下角Y = max(左上角Y, min(右下角Y, 逻辑高度))
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
