import sqlite3
from src.公共.日志管理 import 获取日志管理器


class 配置DAO类:
    """应用配置数据访问对象"""

    def __init__(self, 数据库连接: sqlite3.Connection):
        self.连接 = 数据库连接
        self.日志 = 获取日志管理器("配置DAO")

    def 查询配置(self, 键名: str, 默认值: str = "") -> str:
        """查询配置值，未找到时返回默认值

        参数:
            键名: 配置项键名
            默认值: 未找到时的默认返回值
        """
        结果 = self.连接.execute(
            "SELECT 配置键值 FROM 应用配置表 WHERE 配置键名 = ?",
            (键名,),
        ).fetchone()
        return 结果[0] if 结果 else 默认值

    def 设置配置(self, 键名: str, 键值: str) -> None:
        """设置配置值，不存在则插入，存在则更新（保留自增主键）"""
        self.连接.execute(
            "UPDATE 应用配置表 SET 配置键值 = ? WHERE 配置键名 = ?",
            (键值, 键名),
        )
        if self.连接.total_changes == 0 or self.连接.execute(
            "SELECT changes()"
        ).fetchone()[0] == 0:
            self.连接.execute(
                "INSERT INTO 应用配置表 (配置键名, 配置键值) VALUES (?, ?)",
                (键名, 键值),
            )
        self.连接.commit()

    def 查询所有配置(self) -> dict[str, str]:
        """查询所有配置项"""
        行列表 = self.连接.execute("SELECT 配置键名, 配置键值 FROM 应用配置表").fetchall()
        return {行[0]: 行[1] for 行 in 行列表}