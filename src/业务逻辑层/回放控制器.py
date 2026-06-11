import time
import threading
from PySide6.QtCore import QObject, Signal
from src.公共.数据结构 import 操作步骤数据, 步骤执行结果
from src.公共.枚举定义 import 操作类型枚举, 运行状态枚举, 鼠标操作类型集合, 按键操作类型集合
from src.公共.日志管理 import 获取日志管理器


class 回放控制器类(QObject):
    """操作回放控制器，按步骤序列自动执行操作"""

    步骤执行完成 = Signal(object)
    回放状态变更 = Signal(str, str)
    回放完成 = Signal(bool)

    def __init__(self, 鼠标执行器=None, 按键执行器=None, OCR服务=None, OCR条件判断器=None):
        super().__init__()
        self.鼠标执行器 = 鼠标执行器
        self.按键执行器 = 按键执行器
        self.OCR服务 = OCR服务
        self.OCR条件判断器 = OCR条件判断器
        self.悬浮窗 = None
        self.配置DAO = None
        self._执行线程 = None
        self._停止标志 = False
        self._暂停标志 = False
        self._暂停事件 = threading.Event()
        self._暂停事件.set()
        self.日志 = 获取日志管理器("回放控制器")

    def 启动回放(self, 顶层步骤列表: list[操作步骤数据],
                  步骤树: dict[int, dict[str, list[操作步骤数据]]] | None = None,
                  速度倍率: float = 1.0, 循环次数: int = 1) -> None:
        """启动脚本回放执行

        参数:
            顶层步骤列表: 顶层步骤列表
            步骤树: {父步骤标识: {分支类型: [子步骤列表]}}
            速度倍率: 执行速度倍率
            循环次数: 循环次数
        """
        if self._执行线程 and self._执行线程.is_alive():
            return
        self._停止标志 = False
        self._暂停标志 = False
        self._执行线程 = threading.Thread(
            target=self._回放循环,
            args=(顶层步骤列表, 步骤树 or {}, 速度倍率, 循环次数),
            daemon=True,
        )
        self._执行线程.start()

    def 暂停回放(self) -> None:
        """暂停当前回放"""
        self._暂停标志 = True
        self._暂停事件.clear()

    def 恢复回放(self) -> None:
        """恢复暂停的回放"""
        self._暂停标志 = False
        self._暂停事件.set()

    def 紧急停止(self) -> None:
        """立即终止当前执行，释放所有按下的按键"""
        self._停止标志 = True
        self._暂停标志 = False
        self._暂停事件.set()
        self._释放所有按键()

    def _回放循环(self, 顶层步骤列表: list[操作步骤数据],
                   步骤树: dict[int, dict[str, list[操作步骤数据]]],
                   速度倍率: float, 循环次数: int) -> None:
        """回放主循环，支持树状分支执行"""
        self.回放状态变更.emit("回放中", "")
        try:
            for 循环序号 in range(循环次数):
                if self._停止标志:
                    break
                self._执行步骤树(顶层步骤列表, 步骤树, 速度倍率)
            self.回放完成.emit(not self._停止标志)
        except Exception as 异常:
            self.日志.error(f"回放异常: {异常}")
            self.回放完成.emit(False)
        finally:
            self.回放状态变更.emit("空闲", "")

    def _执行步骤树(self, 步骤列表: list[操作步骤数据],
                      步骤树: dict[int, dict[str, list[操作步骤数据]]],
                      速度倍率: float) -> None:
        """递归执行步骤树，遇到条件判断时走对应分支"""
        for 步骤 in 步骤列表:
            self._暂停事件.wait()
            if self._停止标志:
                break
            结果 = self._执行步骤(步骤)
            self.步骤执行完成.emit(结果)
            if 步骤.步骤延时 > 0:
                self._等待延时(步骤.步骤延时, 速度倍率)
            # 处理子步骤（分支）
            if 步骤.步骤标识 in 步骤树:
                分支字典 = 步骤树[步骤.步骤标识]
                if 结果.执行成功:
                    # 条件满足，执行"是"分支
                    是分支步骤 = 分支字典.get("是", [])
                    if 是分支步骤:
                        self._执行步骤树(是分支步骤, 步骤树, 速度倍率)
                else:
                    # 条件不满足，执行"否"分支
                    否分支步骤 = 分支字典.get("否", [])
                    if 否分支步骤:
                        self._执行步骤树(否分支步骤, 步骤树, 速度倍率)

    def _执行步骤(self, 步骤: 操作步骤数据) -> 步骤执行结果:
        """执行单个操作步骤"""
        开始时间 = time.perf_counter()
        避让中 = False
        try:
            操作类型 = 操作类型枚举(步骤.操作类型)
            避让中 = self._执行避让(步骤, 操作类型)
            if 鼠标操作类型集合.包含(操作类型):
                成功 = self._执行鼠标操作(操作类型, 步骤)
            elif 按键操作类型集合.包含(操作类型):
                成功 = self._执行按键操作(操作类型, 步骤)
            elif 操作类型 == 操作类型枚举.OCR条件判断:
                成功 = self._执行OCR条件判断(步骤)
            elif 操作类型 == 操作类型枚举.延时:
                if 步骤.延时时长:
                    time.sleep(步骤.延时时长 / 1000.0)
                成功 = True
            else:
                成功 = False
            耗时 = int((time.perf_counter() - 开始时间) * 1000)
            return 步骤执行结果(步骤序号=步骤.排序序号, 执行成功=成功, 执行耗时=耗时)
        except Exception as 异常:
            耗时 = int((time.perf_counter() - 开始时间) * 1000)
            return 步骤执行结果(步骤序号=步骤.排序序号, 执行成功=False, 执行耗时=耗时, 错误信息=str(异常))
        finally:
            if 避让中:
                self._恢复悬浮窗()

    def _执行避让(self, 步骤: 操作步骤数据, 操作类型: 操作类型枚举) -> bool:
        """检测并执行悬浮窗自动避让，返回是否正在避让"""
        if not self.悬浮窗 or not self.配置DAO:
            return False
        避让配置 = self.配置DAO.查询配置("悬浮窗自动避让", "false")
        if 避让配置 != "true":
            return False
        目标X = 目标Y = -1
        if 鼠标操作类型集合.包含(操作类型):
            if 操作类型 == 操作类型枚举.鼠标拖拽:
                目标X = 步骤.起点坐标X or 0
                目标Y = 步骤.起点坐标Y or 0
            else:
                目标X = 步骤.目标坐标X or 0
                目标Y = 步骤.目标坐标Y or 0
        elif 操作类型 == 操作类型枚举.OCR条件判断:
            目标X = 步骤.OCR区域左上角X or 0
            目标Y = 步骤.OCR区域左上角Y or 0
        if 目标X >= 0 and self.悬浮窗.检测操作区域冲突(目标X, 目标Y):
            self.悬浮窗.自动避让()
            return True
        return False

    def _恢复悬浮窗(self) -> None:
        """恢复悬浮窗显示"""
        if self.悬浮窗:
            self.悬浮窗.恢复显示()

    def _执行鼠标操作(self, 操作类型: 操作类型枚举, 步骤: 操作步骤数据) -> bool:
        """执行鼠标操作"""
        if not self.鼠标执行器:
            return False
        X = 步骤.目标坐标X or 0
        Y = 步骤.目标坐标Y or 0
        if 操作类型 == 操作类型枚举.鼠标移动:
            return self.鼠标执行器.移动到(X, Y)
        elif 操作类型 == 操作类型枚举.鼠标左键单击:
            return self.鼠标执行器.左键单击(X, Y)
        elif 操作类型 == 操作类型枚举.鼠标左键双击:
            return self.鼠标执行器.左键双击(X, Y)
        elif 操作类型 == 操作类型枚举.鼠标右键单击:
            return self.鼠标执行器.右键单击(X, Y)
        elif 操作类型 == 操作类型枚举.鼠标滚轮上滚:
            return self.鼠标执行器.滚轮滚动(X, Y, 步骤.滚轮量 or 3, "向上")
        elif 操作类型 == 操作类型枚举.鼠标滚轮下滚:
            return self.鼠标执行器.滚轮滚动(X, Y, 步骤.滚轮量 or 3, "向下")
        elif 操作类型 == 操作类型枚举.鼠标拖拽:
            return self.鼠标执行器.拖拽(
                步骤.起点坐标X or 0, 步骤.起点坐标Y or 0,
                步骤.终点坐标X or 0, 步骤.终点坐标Y or 0,
            )
        return False

    def _执行按键操作(self, 操作类型: 操作类型枚举, 步骤: 操作步骤数据) -> bool:
        """执行按键操作"""
        if not self.按键执行器:
            return False
        if 操作类型 == 操作类型枚举.键盘按键:
            return self.按键执行器.单键按下(步骤.按键值 or "")
        elif 操作类型 == 操作类型枚举.键盘组合键:
            修饰键 = (步骤.修饰键列表 or "").split("+") if 步骤.修饰键列表 else []
            return self.按键执行器.组合键(修饰键, 步骤.按键值 or "")
        elif 操作类型 == 操作类型枚举.文本输入:
            return self.按键执行器.文本输入(步骤.输入文本 or "")
        elif 操作类型 == 操作类型枚举.按键保持:
            return self.按键执行器.按键保持(步骤.按键值 or "", 步骤.按键保持时长 or 1000)
        return False

    def _执行OCR条件判断(self, 步骤: 操作步骤数据) -> bool:
        """执行OCR条件判断：识别屏幕区域文字并判断条件，返回条件是否满足"""
        if not self.OCR条件判断器:
            return False
        区域 = (
            步骤.OCR区域左上角X or 0, 步骤.OCR区域左上角Y or 0,
            步骤.OCR区域右下角X or 0, 步骤.OCR区域右下角Y or 0,
        )
        try:
            return self.OCR条件判断器.识别并判断(
                区域=区域,
                条件类型=步骤.OCR条件类型 or "文本匹配",
                目标文本=步骤.OCR目标文本 or "",
                语言=步骤.OCR识别语言 or "中文简体+英文",
                超时时间=步骤.OCR超时时间 or 10,
                轮询间隔=步骤.OCR轮询间隔 or 500,
                超时处理=步骤.OCR超时处理 or "跳过继续",
            )
        except Exception as 异常:
            self.日志.error(f"OCR条件判断执行失败: {异常}")
            return False

    def _等待延时(self, 延时毫秒: int, 速度倍率: float) -> None:
        """按速度倍率等待步骤间延时"""
        实际延时 = 延时毫秒 / 速度倍率 if 速度倍率 > 0 else 延时毫秒
        if 实际延时 > 0:
            time.sleep(实际延时 / 1000.0)

    def _释放所有按键(self) -> None:
        """紧急停止时释放所有按下的按键"""
        try:
            import pyautogui
            pyautogui.keyUp("shift")
            pyautogui.keyUp("ctrl")
            pyautogui.keyUp("alt")
            pyautogui.mouseUp()
        except Exception:
            pass
