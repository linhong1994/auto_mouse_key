from typing import ClassVar
from PySide6.QtCore import QObject, Signal
from src.公共.数据结构 import 热键配置数据
from src.公共.异常定义 import 热键冲突异常, 热键注册失败异常
from src.公共.日志管理 import 获取日志管理器


_PYNPUT_KEY_MAP = {
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
    "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
    "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    "esc": "esc", "escape": "esc",
    "space": "space", "enter": "enter", "return": "enter",
    "tab": "tab", "backspace": "backspace",
    "ctrl_l": "ctrl", "ctrl_r": "ctrl",
    "alt_l": "alt", "alt_r": "alt",
    "shift_l": "shift", "shift_r": "shift",
    "cmd": "cmd", "cmd_l": "cmd", "cmd_r": "cmd",
}


class 热键管理器类(QObject):
    """全局热键管理器"""

    热键触发信号 = Signal(str)

    默认热键配置: ClassVar[dict[str, str]] = {
        "启动录制": "<f9>",
        "停止录制": "<f9>",
        "启动回放": "<f10>",
        "停止回放": "<f10>",
        "紧急停止": "<esc>",
    }

    def __init__(self, 热键DAO=None):
        super().__init__()
        self.热键DAO = 热键DAO
        self._键盘监听器 = None
        self._当前配置: dict[str, str] = {}
        self._当前按下键: set[str] = set()
        self._已触发热键: set[str] = set()
        self.日志 = 获取日志管理器("热键管理器")

    def 注册热键(self, 功能名称: str, 热键组合: str) -> bool:
        """注册全局热键，返回是否注册成功"""
        冲突列表 = self.检测冲突(热键组合)
        if 冲突列表:
            raise 热键冲突异常(f"热键'{热键组合}'已被{冲突列表}占用")
        self._当前配置[功能名称] = 热键组合
        self._重新注册所有热键()
        return True

    def 注销热键(self, 功能名称: str) -> None:
        """注销指定功能的热键"""
        if 功能名称 in self._当前配置:
            del self._当前配置[功能名称]
            self._重新注册所有热键()

    def 检测冲突(self, 热键组合: str) -> list[str]:
        """检测热键是否与已有热键冲突，返回冲突的功能列表"""
        冲突 = []
        for 功能, 组合 in self._当前配置.items():
            if 组合 == 热键组合:
                冲突.append(功能)
        return 冲突

    def 加载配置(self) -> None:
        """从数据库加载热键配置并注册"""
        if self.热键DAO:
            配置列表 = self.热键DAO.查询所有()
            self._当前配置 = {配置.功能名称: 配置.热键组合 for 配置 in 配置列表}
        if not self._当前配置:
            self._当前配置 = dict(self.默认热键配置)
        self._重新注册所有热键()

    def 保存配置(self) -> None:
        """将当前热键配置保存到数据库"""
        if self.热键DAO:
            for 功能名称, 热键组合 in self._当前配置.items():
                self.热键DAO.更新(功能名称, 热键组合)

    def 获取当前配置(self) -> dict[str, str]:
        """获取当前热键配置"""
        return dict(self._当前配置)

    def _重新注册所有热键(self) -> None:
        """重新注册所有热键"""
        self._停止监听()
        if not self._当前配置:
            return
        try:
            from pynput import keyboard
            self._键盘监听器 = keyboard.Listener(
                on_press=self._处理按键按下,
                on_release=self._处理按键释放,
            )
            self._键盘监听器.start()
            self.日志.info(f"全局热键监听已启动，配置: {self._当前配置}")
        except Exception as 异常:
            self.日志.error(f"全局热键注册失败: {异常}")

    def _处理按键按下(self, key) -> None:
        """处理按键按下事件，检测是否匹配已注册热键"""
        键名 = self._获取键名(key)
        if 键名:
            self._当前按下键.add(键名)
            self._检测热键匹配()

    def _处理按键释放(self, key) -> None:
        """处理按键释放事件"""
        键名 = self._获取键名(key)
        if 键名:
            self._当前按下键.discard(键名)
            for 热键组合 in list(self._已触发热键):
                if 键名 in 热键组合:
                    self._已触发热键.discard(热键组合)

    def _检测热键匹配(self) -> None:
        """检测当前按下的键是否匹配已注册的热键组合"""
        for 功能名称, 热键组合 in self._当前配置.items():
            if 热键组合 in self._已触发热键:
                continue
            要求键集 = self._解析热键组合(热键组合)
            if 要求键集 and 要求键集.issubset(self._当前按下键):
                self._已触发热键.add(热键组合)
                self._安全发射热键信号(功能名称)

    def _解析热键组合(self, 热键组合: str) -> set[str]:
        """解析热键组合字符串为键名集合

        例如: "<ctrl>+<f9>" -> {"ctrl", "f9"}
              "<f9>" -> {"f9"}
        """
        键集 = set()
        部分 = 热键组合.split("+")
        for 部分_ in 部分:
            部分_ = 部分_.strip()
            if 部分_.startswith("<") and 部分_.endswith(">"):
                键名 = 部分_[1:-1]
            else:
                键名 = 部分_
            键集.add(键名.lower())
        return 键集

    def _获取键名(self, key) -> str | None:
        """从pynput按键对象获取标准化键名"""
        try:
            from pynput import keyboard
            if isinstance(key, keyboard.Key):
                原名 = key.name.lower()
                return _PYNPUT_KEY_MAP.get(原名, 原名)
            elif isinstance(key, keyboard.KeyCode):
                if key.char:
                    return key.char.lower()
                elif key.vk:
                    vk映射 = {
                        112: "f1", 113: "f2", 114: "f3", 115: "f4",
                        116: "f5", 117: "f6", 118: "f7", 119: "f8",
                        120: "f9", 121: "f10", 122: "f11", 123: "f12",
                    }
                    return vk映射.get(key.vk, None)
        except Exception:
            pass
        return None

    def _安全发射热键信号(self, 功能名称: str) -> None:
        """在主线程中安全发射热键触发信号

        pynput回调在子线程执行，Qt信号必须在主线程发射
        """
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.热键触发信号.emit(功能名称))

    def _停止监听(self) -> None:
        """停止键盘监听"""
        if self._键盘监听器:
            try:
                self._键盘监听器.stop()
            except Exception:
                pass
            self._键盘监听器 = None
        self._当前按下键.clear()
        self._已触发热键.clear()

    def 停止(self) -> None:
        """停止热键管理器"""
        self._停止监听()
