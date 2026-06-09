import time
from src.公共.数据结构 import OCR识别结果, OCR触发条件
from src.公共.异常定义 import OCR条件超时异常
from src.公共.日志管理 import 获取日志管理器


class OCR条件判断器类:
    """根据OCR识别结果判断触发条件"""

    def __init__(self, OCR服务=None):
        self.OCR服务 = OCR服务
        self.日志 = 获取日志管理器("OCR条件判断器")

    def 判断条件(self, 条件列表: list[OCR触发条件], 逻辑关系: str = "与") -> bool:
        """判断多个OCR触发条件是否满足

        参数:
            条件列表: OCR触发条件列表
            逻辑关系: 多条件逻辑关系，"与"或"或"
        """
        if not 条件列表:
            return True
        结果列表 = []
        for 条件 in 条件列表:
            识别结果 = self._识别区域(条件.识别区域, 条件.识别语言)
            if 识别结果 is None:
                结果列表.append(False)
                continue
            单条结果 = self._判断单条件(条件, 识别结果)
            结果列表.append(单条结果)
        if 逻辑关系 == "或":
            return any(结果列表)
        return all(结果列表)

    def 文本匹配(self, 识别结果: OCR识别结果, 目标文本: str) -> bool:
        """判断识别结果是否完全匹配目标文本"""
        return 识别结果.识别文本.strip() == 目标文本.strip()

    def 文本包含(self, 识别结果: OCR识别结果, 关键词: str) -> bool:
        """判断识别结果是否包含指定关键词"""
        return 关键词 in 识别结果.识别文本

    def 文字变化检测(self, 当前结果: OCR识别结果, 上次结果: OCR识别结果) -> bool:
        """判断指定区域文字内容是否发生变化"""
        return 当前结果.识别文本 != 上次结果.识别文本

    def 轮询检测(self, 条件: OCR触发条件, 超时时间: int = 10, 轮询间隔: int = 500) -> bool:
        """以指定间隔轮询检测OCR条件直到满足或超时

        参数:
            条件: OCR触发条件
            超时时间: 超时时间，秒
            轮询间隔: 轮询间隔，毫秒，最小200
        """
        轮询间隔 = max(轮询间隔, 200)
        开始时间 = time.time()
        上次结果 = None
        while True:
            识别结果 = self._识别区域(条件.识别区域, 条件.识别语言)
            if 识别结果 is not None:
                if 条件.条件类型 == "文字变化" and 上次结果 is not None:
                    满足 = self.文字变化检测(识别结果, 上次结果)
                else:
                    满足 = self._判断单条件(条件, 识别结果)
                if 满足:
                    return True
                上次结果 = 识别结果
            已等待 = time.time() - 开始时间
            if 已等待 >= 超时时间:
                if 条件.超时处理 == "停止脚本":
                    raise OCR条件超时异常(f"OCR条件检测超时({超时时间}秒)")
                return False
            time.sleep(轮询间隔 / 1000.0)

    def _判断单条件(self, 条件: OCR触发条件, 识别结果: OCR识别结果) -> bool:
        """判断单个OCR触发条件"""
        if 条件.条件类型 == "文本匹配":
            return self.文本匹配(识别结果, 条件.目标文本)
        elif 条件.条件类型 == "文本不匹配":
            return not self.文本匹配(识别结果, 条件.目标文本)
        elif 条件.条件类型 == "文本包含":
            return self.文本包含(识别结果, 条件.目标文本)
        elif 条件.条件类型 == "文字变化":
            return False
        return False

    def _识别区域(self, 区域: tuple[int, int, int, int], 语言: str) -> OCR识别结果 | None:
        """调用OCR服务识别指定区域"""
        if self.OCR服务 is None:
            return None
        try:
            return self.OCR服务.识别区域(区域[0], 区域[1], 区域[2], 区域[3], 语言)
        except Exception as 异常:
            self.日志.warning(f"OCR识别失败: {异常}")
            return None