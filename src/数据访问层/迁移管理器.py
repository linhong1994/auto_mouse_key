import sqlite3
from datetime import datetime
from typing import Callable
from src.公共.异常定义 import 数据库迁移失败异常
from src.公共.日志管理 import 获取日志管理器


class 迁移管理器类:
    """数据库Schema版本迁移管理器"""

    def __init__(self, 数据库连接: sqlite3.Connection):
        self.连接 = 数据库连接
        self.迁移脚本注册表: dict[int, Callable] = {}
        self.日志 = 获取日志管理器("迁移管理器")
        self._注册所有迁移脚本()

    def 获取当前版本(self) -> int:
        """获取数据库当前schema版本号"""
        try:
            结果 = self.连接.execute("SELECT 版本号 FROM Schema版本表 WHERE 版本标识 = 1").fetchone()
            return 结果[0] if 结果 else 0
        except sqlite3.Error:
            return 0

    def 执行迁移(self, 目标版本: int) -> None:
        """执行数据库迁移到目标版本

        参数:
            目标版本: 目标schema版本号
        """
        当前版本 = self.获取当前版本()
        if 当前版本 >= 目标版本:
            return
        try:
            for 版本 in range(当前版本 + 1, 目标版本 + 1):
                if 版本 in self.迁移脚本注册表:
                    self.迁移脚本注册表[版本]()
                    self.日志.info(f"迁移到版本{版本}完成")
            self.连接.execute(
                "UPDATE Schema版本表 SET 版本号 = ?, 更新时间 = ? WHERE 版本标识 = 1",
                (目标版本, datetime.now().isoformat()),
            )
            self.连接.commit()
        except Exception as 异常:
            self.连接.rollback()
            self.日志.error(f"迁移到版本{目标版本}失败: {异常}")
            raise 数据库迁移失败异常(f"迁移到版本{目标版本}失败: {异常}", 异常)

    def _注册所有迁移脚本(self) -> None:
        """注册所有版本的迁移脚本，后续版本按需添加"""
        pass