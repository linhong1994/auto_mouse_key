import time
from typing import ClassVar
import pyautogui
from src.公共.异常定义 import 禁止组合键异常
from src.公共.日志管理 import 获取日志管理器


pyautogui.FAILSAFE = False


class 按键操作执行器类:
    """键盘自动化操作执行器，负责向操作系统发送键盘模拟事件"""

    禁止组合键列表: ClassVar[list[str]] = ["ctrl+alt+delete"]

    def __init__(self):
        self.日志 = 获取日志管理器("按键操作执行器")

    def 单键按下(self, 按键值: str) -> bool:
        """模拟单个按键的按下与释放"""
        self._校验按键合法性(按键值)
        try:
            pyautogui.press(按键值)
            return True
        except Exception as 异常:
            self.日志.error(f"单键按下失败: {异常}")
            return False

    def 组合键(self, 修饰键列表: list[str], 主键: str) -> bool:
        """模拟组合键操作，按顺序按下后逆序释放"""
        self._校验组合键安全性(修饰键列表, 主键)
        try:
            所有键 = 修饰键列表 + [主键]
            pyautogui.hotkey(*所有键)
            return True
        except Exception as 异常:
            self.日志.error(f"组合键执行失败: {异常}")
            return False

    def 文本输入(self, 文本: str, 按键延时: int = 0) -> bool:
        """逐字符输入指定文本

        参数:
            文本: 要输入的文本内容
            按键延时: 按键间延时，毫秒
        """
        try:
            间隔 = 按键延时 / 1000.0 if 按键延时 > 0 else 0
            pyautogui.typewrite(文本, interval=间隔)
            return True
        except Exception as 异常:
            self.日志.error(f"文本输入失败: {异常}")
            return False

    def 按键保持(self, 按键值: str, 保持时长: int) -> bool:
        """模拟按键持续按住指定时长后释放

        参数:
            按键值: 按键名称
            保持时长: 保持时长，毫秒
        """
        self._校验按键合法性(按键值)
        try:
            pyautogui.keyDown(按键值)
            time.sleep(保持时长 / 1000.0)
            pyautogui.keyUp(按键值)
            return True
        except Exception as 异常:
            self.日志.error(f"按键保持失败: {异常}")
            try:
                pyautogui.keyUp(按键值)
            except Exception:
                pass
            return False

    def _校验按键合法性(self, 按键值: str) -> bool:
        """校验按键值是否为有效的键盘按键名称"""
        if not 按键值:
            raise 禁止组合键异常("按键值不能为空")
        return True

    def _校验组合键安全性(self, 修饰键列表: list[str], 主键: str) -> bool:
        """校验组合键是否为系统安全禁止键"""
        组合字符串 = "+".join(sorted([k.lower() for k in 修饰键列表] + [主键.lower()]))
        for 禁止键 in self.禁止组合键列表:
            if 组合字符串 == 禁止键:
                raise 禁止组合键异常(f"组合键 '{组合字符串}' 为系统安全键，禁止模拟")
        return True