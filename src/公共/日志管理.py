import logging
import os
from logging.handlers import TimedRotatingFileHandler


_日志管理器实例: logging.Logger | None = None


def 获取日志管理器(模块名: str = "自动操作工具") -> logging.Logger:
    """获取指定模块的日志记录器

    参数:
        模块名: 模块名称，用于区分不同模块的日志

    返回:
        配置好的Logger实例
    """
    global _日志管理器实例
    if _日志管理器实例 is None:
        _初始化日志管理器()
    return _日志管理器实例.getChild(模块名)


def _初始化日志管理器() -> None:
    """初始化全局日志管理器，配置按日期分割的日志文件"""
    global _日志管理器实例

    _日志管理器实例 = logging.getLogger("自动操作工具")
    _日志管理器实例.setLevel(logging.DEBUG)

    日志目录 = os.path.join(os.path.expanduser("~"), "AppData", "Local", "auto_mouse_key", "logs")
    os.makedirs(日志目录, exist_ok=True)

    日志文件路径 = os.path.join(日志目录, "auto_mouse_key.log")

    文件处理器 = TimedRotatingFileHandler(
        日志文件路径,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    文件处理器.suffix = "%Y-%m-%d.log"
    文件处理器.setLevel(logging.DEBUG)

    文件格式化器 = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    文件处理器.setFormatter(文件格式化器)

    控制台处理器 = logging.StreamHandler()
    控制台处理器.setLevel(logging.INFO)

    控制台格式化器 = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    控制台处理器.setFormatter(控制台格式化器)

    _日志管理器实例.addHandler(文件处理器)
    _日志管理器实例.addHandler(控制台处理器)