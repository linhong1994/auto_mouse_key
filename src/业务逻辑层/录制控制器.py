import time
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from src.公共.数据结构 import 操作步骤数据
from src.公共.枚举定义 import 操作类型枚举, 运行状态枚举
from src.公共.日志管理 import 获取日志管理器

鼠标移动节流间隔 = 0.3
双击间隔阈值 = 0.3
拖拽距离阈值 = 5
修饰键集合 = {"alt", "alt_l", "alt_r", "ctrl", "ctrl_l", "ctrl_r",
             "shift", "shift_l", "shift_r", "cmd", "cmd_l", "cmd_r", "super"}


class 录制控制器类(QObject):
    """操作录制控制器，监听并捕获用户操作"""

    录制步骤捕获 = Signal(object)
    录制状态变更 = Signal(bool)

    def __init__(self, 脚本管理服务=None, 步骤管理服务=None):
        super().__init__()
        self.脚本管理服务 = 脚本管理服务
        self.步骤管理服务 = 步骤管理服务
        self._录制中 = False
        self._已捕获步骤: list[操作步骤数据] = []
        self._上一步时间戳: float = 0.0
        self._鼠标监听器 = None
        self._键盘监听器 = None
        self._当前按下修饰键: set[str] = set()
        self._上次点击时间: float = 0.0
        self._上次点击坐标: tuple[int, int] = (0, 0)
        self._上次点击按钮: str = ""
        self._拖拽起始坐标: tuple[int, int] | None = None
        self._拖拽按钮: str = ""
        self._文本缓冲: str = ""
        self._文本缓冲起始时间: float = 0.0
        self._上次移动时间: float = 0.0
        self._上次移动坐标: tuple[int, int] | None = None
        self.日志 = 获取日志管理器("录制控制器")

    def 启动录制(self) -> None:
        """进入录制模式，开始监听鼠标/键盘事件"""
        if self._录制中:
            return
        self._录制中 = True
        self._已捕获步骤 = []
        self._上一步时间戳 = time.perf_counter()
        self._当前按下修饰键 = set()
        self._上次点击时间 = 0.0
        self._上次点击坐标 = (0, 0)
        self._上次点击按钮 = ""
        self._拖拽起始坐标 = None
        self._文本缓冲 = ""
        self._文本缓冲起始时间 = 0.0
        self._上次移动时间 = 0.0
        self._上次移动坐标 = None
        try:
            from pynput import mouse, keyboard
            self._鼠标监听器 = mouse.Listener(
                on_click=self._处理鼠标点击,
                on_scroll=self._处理鼠标滚轮,
                on_move=self._处理鼠标移动,
            )
            self._键盘监听器 = keyboard.Listener(
                on_press=self._处理键盘按下,
                on_release=self._处理键盘释放,
            )
            self._鼠标监听器.start()
            self._键盘监听器.start()
            self.录制状态变更.emit(True)
            self.日志.info("录制已启动")
        except Exception as 异常:
            self._录制中 = False
            self.日志.error(f"录制启动失败: {异常}")

    def 停止录制(self) -> int | None:
        """停止录制，保存脚本及步骤到数据库，返回脚本标识"""
        if not self._录制中:
            return None
        self._录制中 = False
        self._刷新文本缓冲()
        self._刷新末次移动()
        if self._鼠标监听器:
            self._鼠标监听器.stop()
            self._鼠标监听器 = None
        if self._键盘监听器:
            self._键盘监听器.stop()
            self._键盘监听器 = None
        self.录制状态变更.emit(False)
        self.日志.info(f"录制已停止，共捕获{len(self._已捕获步骤)}个步骤")
        return self._保存录制结果()

    def 是否录制中(self) -> bool:
        """查询当前是否处于录制模式"""
        return self._录制中

    def _处理鼠标点击(self, x, y, button, pressed) -> None:
        """处理捕获的鼠标点击事件，支持双击检测和拖拽检测"""
        if not self._录制中:
            return
        按钮名 = button.name
        if pressed:
            self._拖拽起始坐标 = (x, y)
            self._拖拽按钮 = 按钮名
            return
        if self._拖拽起始坐标 is not None:
            起始X, 起始Y = self._拖拽起始坐标
            距离 = ((x - 起始X) ** 2 + (y - 起始Y) ** 2) ** 0.5
            if 距离 >= 拖拽距离阈值:
                self._刷新文本缓冲()
                self._记录步骤(
                    操作类型枚举.鼠标拖拽.value,
                    起点坐标X=起始X, 起点坐标Y=起始Y,
                    终点坐标X=x, 终点坐标Y=y,
                )
                self._拖拽起始坐标 = None
                return
            self._拖拽起始坐标 = None
        当前时间 = time.perf_counter()
        if (按钮名 == self._上次点击按钮
                and 当前时间 - self._上次点击时间 < 双击间隔阈值
                and abs(x - self._上次点击坐标[0]) < 5
                and abs(y - self._上次点击坐标[1]) < 5):
            self._刷新文本缓冲()
            if 按钮名 == "left":
                self._记录步骤(操作类型枚举.鼠标左键双击.value, 目标坐标X=x, 目标坐标Y=y)
            self._上次点击时间 = 0.0
            self._上次点击按钮 = ""
            return
        self._刷新文本缓冲()
        if 按钮名 == "left":
            操作类型 = 操作类型枚举.鼠标左键单击.value
        elif 按钮名 == "right":
            操作类型 = 操作类型枚举.鼠标右键单击.value
        else:
            return
        self._记录步骤(操作类型, 目标坐标X=x, 目标坐标Y=y)
        self._上次点击时间 = 当前时间
        self._上次点击坐标 = (x, y)
        self._上次点击按钮 = 按钮名

    def _处理鼠标滚轮(self, x, y, dx, dy) -> None:
        """处理捕获的鼠标滚轮事件"""
        if not self._录制中:
            return
        self._刷新文本缓冲()
        if dy > 0:
            操作类型 = 操作类型枚举.鼠标滚轮上滚.value
        elif dy < 0:
            操作类型 = 操作类型枚举.鼠标滚轮下滚.value
        else:
            return
        self._记录步骤(操作类型, 目标坐标X=x, 目标坐标Y=y, 滚轮量=abs(dy))

    def _处理鼠标移动(self, x, y) -> None:
        """处理捕获的鼠标移动事件，带节流"""
        if not self._录制中:
            return
        当前时间 = time.perf_counter()
        if 当前时间 - self._上次移动时间 < 鼠标移动节流间隔:
            self._上次移动坐标 = (x, y)
            return
        if self._上次移动坐标 is not None:
            self._刷新文本缓冲()
            self._记录步骤(
                操作类型枚举.鼠标移动.value,
                目标坐标X=self._上次移动坐标[0],
                目标坐标Y=self._上次移动坐标[1],
            )
        self._上次移动时间 = 当前时间
        self._上次移动坐标 = (x, y)

    def _处理键盘按下(self, key) -> None:
        """处理捕获的键盘按下事件，区分修饰键、组合键和普通字符"""
        if not self._录制中:
            return
        按键名称 = self._获取按键名称(key)
        if not 按键名称:
            return
        if 按键名称 in 修饰键集合:
            self._当前按下修饰键.add(按键名称)
            return
        if self._当前按下修饰键:
            self._刷新文本缓冲()
            修饰键列表 = sorted(self._当前按下修饰键)
            self._记录步骤(
                操作类型枚举.键盘组合键.value,
                按键值=按键名称,
                修饰键列表="+".join(修饰键列表),
            )
            return
        字符 = self._获取字符(key)
        if 字符:
            当前时间 = time.perf_counter()
            if not self._文本缓冲:
                self._文本缓冲起始时间 = 当前时间
            self._文本缓冲 += 字符
            return
        self._刷新文本缓冲()
        self._记录步骤(操作类型枚举.键盘按键.value, 按键值=按键名称)

    def _处理键盘释放(self, key) -> None:
        """处理键盘释放事件，移除修饰键"""
        if not self._录制中:
            return
        按键名称 = self._获取按键名称(key)
        if 按键名称 and 按键名称 in 修饰键集合:
            self._当前按下修饰键.discard(按键名称)

    def _刷新文本缓冲(self) -> None:
        """将文本缓冲区内容刷新为文本输入步骤"""
        if self._文本缓冲:
            self._记录步骤(操作类型枚举.文本输入.value, 输入文本=self._文本缓冲)
            self._文本缓冲 = ""

    def _刷新末次移动(self) -> None:
        """将末次鼠标移动坐标刷新为步骤"""
        if self._上次移动坐标 is not None:
            self._记录步骤(
                操作类型枚举.鼠标移动.value,
                目标坐标X=self._上次移动坐标[0],
                目标坐标Y=self._上次移动坐标[1],
            )
            self._上次移动坐标 = None

    def _记录步骤(self, 操作类型: str, **参数) -> None:
        """记录一个操作步骤"""
        当前时间 = time.perf_counter()
        延时 = self._计算步骤延时(当前时间, self._上一步时间戳)
        self._上一步时间戳 = 当前时间
        步骤 = 操作步骤数据(
            操作类型=操作类型,
            排序序号=len(self._已捕获步骤) + 1,
            步骤延时=延时,
            **参数,
        )
        self._已捕获步骤.append(步骤)
        self.录制步骤捕获.emit(步骤)

    def _计算步骤延时(self, 当前时间戳: float, 上一步时间戳: float) -> int:
        """计算当前步骤与上一步的时间间隔作为延时，毫秒"""
        return int((当前时间戳 - 上一步时间戳) * 1000)

    def _获取按键名称(self, key) -> str | None:
        """从pynput按键对象获取按键名称"""
        try:
            from pynput import keyboard
            if isinstance(key, keyboard.Key):
                return key.name
            elif isinstance(key, keyboard.KeyCode):
                return key.char if key.char else str(key)
        except Exception:
            pass
        return None

    def _获取字符(self, key) -> str | None:
        """从pynput按键对象获取可打印字符"""
        try:
            from pynput import keyboard
            if isinstance(key, keyboard.KeyCode) and key.char and key.char.isprintable():
                return key.char
        except Exception:
            pass
        return None

    def _保存录制结果(self) -> int | None:
        """保存录制结果到数据库"""
        if not self._已捕获步骤 or not self.脚本管理服务 or not self.步骤管理服务:
            return None
        try:
            脚本名称 = f"录制脚本_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            脚本标识 = self.脚本管理服务.创建脚本(脚本名称, "")
            for 步骤 in self._已捕获步骤:
                步骤.所属脚本标识 = 脚本标识
                self.步骤管理服务.添加步骤(脚本标识, 步骤)
            self.日志.info(f"录制结果已保存，脚本标识: {脚本标识}")
            return 脚本标识
        except Exception as 异常:
            self.日志.error(f"保存录制结果失败: {异常}")
            return None
