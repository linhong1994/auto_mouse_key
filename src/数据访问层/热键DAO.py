import sqlite3
from src.公共.数据结构 import 热键配置数据
from src.公共.日志管理 import 获取日志管理器


class 热键DAO类:
    """热键配置数据访问对象"""

    def __init__(self, 数据库连接: sqlite3.Connection):
        self.连接 = 数据库连接
        self.日志 = 获取日志管理器("热键DAO")

    def 查询所有(self) -> list[热键配置数据]:
        """查询所有热键配置"""
        行列表 = self.连接.execute("SELECT * FROM 热键配置表 ORDER BY 配置标识 ASC").fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 更新(self, 功能名称: str, 热键组合: str) -> None:
        """更新指定功能的热键组合"""
        self.连接.execute(
            "UPDATE 热键配置表 SET 热键组合 = ? WHERE 功能名称 = ?",
            (热键组合, 功能名称),
        )
        self.连接.commit()

    def 初始化默认配置(self) -> None:
        """初始化默认热键配置（已由数据库管理器在初始化时处理）"""
        pass

    def _行转数据(self, 行: sqlite3.Row) -> 热键配置数据:
        """将数据库行转换为热键配置数据"""
        return 热键配置数据(
            配置标识=行["配置标识"],
            功能名称=行["功能名称"],
            热键组合=行["热键组合"],
            全局生效=bool(行["全局生效"]),
        )