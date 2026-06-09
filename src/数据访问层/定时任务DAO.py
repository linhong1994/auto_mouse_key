import sqlite3
from src.公共.数据结构 import 定时任务数据
from src.公共.日志管理 import 获取日志管理器


class 定时任务DAO类:
    """定时任务数据访问对象"""

    def __init__(self, 数据库连接: sqlite3.Connection):
        self.连接 = 数据库连接
        self.日志 = 获取日志管理器("定时任务DAO")

    def 插入(self, 数据: 定时任务数据) -> int:
        """插入定时任务记录，返回任务标识"""
        游标 = self.连接.execute(
            """INSERT INTO 定时任务表
            (任务名称, 关联脚本标识, 触发类型, 触发时间, 循环间隔, 每日时间, 启用状态, 任务状态)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (数据.任务名称, 数据.关联脚本标识, 数据.触发类型, 数据.触发时间,
             数据.循环间隔, 数据.每日时间, 1 if 数据.启用状态 else 0, 数据.任务状态),
        )
        self.连接.commit()
        return 游标.lastrowid

    def 查询所有(self) -> list[定时任务数据]:
        """查询所有定时任务"""
        行列表 = self.连接.execute("SELECT * FROM 定时任务表 ORDER BY 任务标识 ASC").fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 查询启用的任务(self) -> list[定时任务数据]:
        """查询所有启用的定时任务"""
        行列表 = self.连接.execute(
            "SELECT * FROM 定时任务表 WHERE 启用状态 = 1 ORDER BY 任务标识 ASC"
        ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 更新(self, 标识: int, 数据: 定时任务数据) -> None:
        """更新定时任务"""
        self.连接.execute(
            """UPDATE 定时任务表 SET
            任务名称 = ?, 关联脚本标识 = ?, 触发类型 = ?, 触发时间 = ?,
            循环间隔 = ?, 每日时间 = ?, 启用状态 = ?, 任务状态 = ?
            WHERE 任务标识 = ?""",
            (数据.任务名称, 数据.关联脚本标识, 数据.触发类型, 数据.触发时间,
             数据.循环间隔, 数据.每日时间, 1 if 数据.启用状态 else 0, 数据.任务状态, 标识),
        )
        self.连接.commit()

    def 删除(self, 标识: int) -> None:
        """删除定时任务"""
        self.连接.execute("DELETE FROM 定时任务表 WHERE 任务标识 = ?", (标识,))
        self.连接.commit()

    def 按脚本查询(self, 脚本标识: int) -> list[定时任务数据]:
        """按关联脚本查询定时任务"""
        行列表 = self.连接.execute(
            "SELECT * FROM 定时任务表 WHERE 关联脚本标识 = ?",
            (脚本标识,),
        ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def _行转数据(self, 行: sqlite3.Row) -> 定时任务数据:
        """将数据库行转换为定时任务数据"""
        return 定时任务数据(
            任务标识=行["任务标识"],
            任务名称=行["任务名称"],
            关联脚本标识=行["关联脚本标识"],
            触发类型=行["触发类型"],
            触发时间=行["触发时间"],
            循环间隔=行["循环间隔"],
            每日时间=行["每日时间"],
            启用状态=bool(行["启用状态"]),
            任务状态=行["任务状态"],
        )