import pyautogui
from src.公共.异常定义 import 坐标超出范围异常
from src.公共.日志管理 import 获取日志管理器


pyautogui.FAILSAFE = False


class 鼠标操作执行器类:
    """鼠标自动化操作执行器，负责向操作系统发送鼠标模拟事件"""

    def __init__(self):
        self.日志 = 获取日志管理器("鼠标操作执行器")

    def 移动到(self, 目标坐标X: int, 目标坐标Y: int, 轨迹模式: str = "直线") -> bool:
        """将鼠标光标移动到指定坐标

        参数:
            目标坐标X: 目标X坐标
            目标坐标Y: 目标Y坐标
            轨迹模式: 移动轨迹模式，"直线"或"缓动"
        返回: 执行是否成功
        """
        self._校验坐标范围(目标坐标X, 目标坐标Y)
        try:
            if 轨迹模式 == "缓动":
                当前X, 当前Y = pyautogui.position()
                self._缓动移动(当前X, 当前Y, 目标坐标X, 目标坐标Y)
            else:
                pyautogui.moveTo(目标坐标X, 目标坐标Y, duration=0)
            return True
        except Exception as 异常:
            self.日志.error(f"鼠标移动失败: {异常}")
            return False

    def 左键单击(self, 坐标X: int, 坐标Y: int) -> bool:
        """在指定坐标执行鼠标左键单击"""
        self._校验坐标范围(坐标X, 坐标Y)
        try:
            pyautogui.click(坐标X, 坐标Y, button="left")
            return True
        except Exception as 异常:
            self.日志.error(f"鼠标左键单击失败: {异常}")
            return False

    def 左键双击(self, 坐标X: int, 坐标Y: int) -> bool:
        """在指定坐标执行鼠标左键双击"""
        self._校验坐标范围(坐标X, 坐标Y)
        try:
            pyautogui.doubleClick(坐标X, 坐标Y, button="left")
            return True
        except Exception as 异常:
            self.日志.error(f"鼠标左键双击失败: {异常}")
            return False

    def 右键单击(self, 坐标X: int, 坐标Y: int) -> bool:
        """在指定坐标执行鼠标右键单击"""
        self._校验坐标范围(坐标X, 坐标Y)
        try:
            pyautogui.click(坐标X, 坐标Y, button="right")
            return True
        except Exception as 异常:
            self.日志.error(f"鼠标右键单击失败: {异常}")
            return False

    def 滚轮滚动(self, 坐标X: int, 坐标Y: int, 滚动量: int, 方向: str = "向下") -> bool:
        """在指定坐标执行鼠标滚轮滚动

        参数:
            坐标X: 目标X坐标
            坐标Y: 目标Y坐标
            滚动量: 滚动量
            方向: 滚动方向，"向上"或"向下"
        """
        self._校验坐标范围(坐标X, 坐标Y)
        try:
            pyautogui.moveTo(坐标X, 坐标Y, duration=0)
            方向值 = -1 if 方向 == "向上" else 1
            pyautogui.scroll(方向值 * 滚动量, 坐标X, 坐标Y)
            return True
        except Exception as 异常:
            self.日志.error(f"鼠标滚轮滚动失败: {异常}")
            return False

    def 拖拽(self, 起点X: int, 起点Y: int, 终点X: int, 终点Y: int) -> bool:
        """从起点坐标拖拽到终点坐标"""
        self._校验坐标范围(起点X, 起点Y)
        self._校验坐标范围(终点X, 终点Y)
        try:
            pyautogui.moveTo(起点X, 起点Y, duration=0)
            pyautogui.drag(终点X - 起点X, 终点Y - 起点Y, duration=0.3, button="left")
            return True
        except Exception as 异常:
            self.日志.error(f"鼠标拖拽失败: {异常}")
            return False

    def _校验坐标范围(self, 坐标X: int, 坐标Y: int) -> bool:
        """校验坐标是否在屏幕有效范围内"""
        屏幕宽度, 屏幕高度 = pyautogui.size()
        if 坐标X < 0 or 坐标X >= 屏幕宽度 or 坐标Y < 0 or 坐标Y >= 屏幕高度:
            raise 坐标超出范围异常(f"坐标({坐标X}, {坐标Y})超出屏幕范围({屏幕宽度}x{屏幕高度})")
        return True

    def _缓动移动(self, 起点X: int, 起点Y: int, 终点X: int, 终点Y: int) -> None:
        """以缓动曲线移动鼠标到目标位置"""
        pyautogui.moveTo(终点X, 终点Y, duration=0.5)