from typing import ClassVar
from PySide6.QtCore import QObject, Signal
from src.公共.数据结构 import 热键配置数据
from src.公共.异常定义 import 热键冲突异常, 热键注册失败异常
from src.公共.日志管理 import 获取日志管理器


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
        self._热键监听器 = None
        self._当前配置: dict[str, str] = {}
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
            热键映射 = {}
            for 功能名称, 热键组合 in self._当前配置.items():
                热键映射[热键组合] = lambda 功能=功能名称: self._安全发射热键信号(功能)
            self._热键监听器 = keyboard.GlobalHotKeys(热键映射)
            self._热键监听器.start()
            self.日志.info("全局热键注册成功")
        except Exception as 异常:
            self.日志.error(f"全局热键注册失败: {异常}")

    def _安全发射热键信号(self, 功能名称: str) -> None:
        """在主线程中安全发射热键触发信号

        pynput回调在子线程执行，Qt信号必须在主线程发射
        """
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.热键触发信号.emit(功能名称))

    def _停止监听(self) -> None:
        """停止热键监听"""
        if self._热键监听器:
            try:
                self._热键监听器.stop()
            except Exception:
                pass
            self._热键监听器 = None

    def 停止(self) -> None:
        """停止热键管理器"""
        self._停止监听()