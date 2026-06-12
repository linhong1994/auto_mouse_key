import sqlite3
from src.公共.数据结构 import 脚本表数据, 脚本概要信息
from src.公共.日志管理 import 获取日志管理器


class 脚本DAO类:
    """脚本数据访问对象"""

    def __init__(self, 数据库连接: sqlite3.Connection):
        self.连接 = 数据库连接
        self.日志 = 获取日志管理器("脚本DAO")

    def 插入(self, 数据: 脚本表数据) -> int:
        """插入脚本记录，返回脚本标识"""
        游标 = self.连接.execute(
            """INSERT INTO 脚本表 (脚本名称, 脚本描述, 创建时间, 修改时间, 定时触发类型, 定时触发时间, 定时循环间隔, 定时每日时间, 定时启用)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (数据.脚本名称, 数据.脚本描述, 数据.创建时间, 数据.修改时间,
             数据.定时触发类型, 数据.定时触发时间, 数据.定时循环间隔, 数据.定时每日时间,
             1 if 数据.定时启用 else 0),
        )
        self.连接.commit()
        return 游标.lastrowid

    def 查询ById(self, 标识: int) -> 脚本表数据 | None:
        """根据标识查询脚本"""
        行 = self.连接.execute("SELECT * FROM 脚本表 WHERE 脚本标识 = ?", (标识,)).fetchone()
        if 行 is None:
            return None
        return self._行转数据(行)

    def 查询所有(self, 排序字段: str = "修改时间", 排序方向: str = "DESC") -> list[脚本表数据]:
        """查询所有脚本"""
        合法字段 = {"脚本标识", "脚本名称", "创建时间", "修改时间"}
        合法方向 = {"ASC", "DESC"}
        if 排序字段 not in 合法字段:
            排序字段 = "修改时间"
        if 排序方向.upper() not in 合法方向:
            排序方向 = "DESC"
        行列表 = self.连接.execute(f"SELECT * FROM 脚本表 ORDER BY {排序字段} {排序方向}").fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 按名称模糊查询(self, 关键词: str) -> list[脚本表数据]:
        """按脚本名称模糊搜索"""
        行列表 = self.连接.execute(
            "SELECT * FROM 脚本表 WHERE 脚本名称 LIKE ? ORDER BY 修改时间 DESC",
            (f"%{关键词}%",),
        ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 更新(self, 标识: int, 数据: 脚本表数据) -> None:
        """更新脚本信息"""
        self.连接.execute(
            """UPDATE 脚本表 SET 脚本名称 = ?, 脚本描述 = ?, 修改时间 = ?,
            定时触发类型 = ?, 定时触发时间 = ?, 定时循环间隔 = ?, 定时每日时间 = ?, 定时启用 = ?
            WHERE 脚本标识 = ?""",
            (数据.脚本名称, 数据.脚本描述, 数据.修改时间,
             数据.定时触发类型, 数据.定时触发时间, 数据.定时循环间隔, 数据.定时每日时间,
             1 if 数据.定时启用 else 0, 标识),
        )
        self.连接.commit()

    def 删除(self, 标识: int) -> None:
        """删除脚本（关联步骤通过外键级联删除）"""
        self.连接.execute("DELETE FROM 脚本表 WHERE 脚本标识 = ?", (标识,))
        self.连接.commit()

    def 统计步骤数量(self, 脚本标识: int) -> int:
        """统计脚本的步骤数量"""
        结果 = self.连接.execute(
            "SELECT COUNT(*) FROM 操作步骤表 WHERE 所属脚本标识 = ?",
            (脚本标识,),
        ).fetchone()
        return 结果[0] if 结果 else 0

    def 查询概要列表(self, 排序字段: str = "修改时间", 排序方向: str = "DESC") -> list[脚本概要信息]:
        """查询所有脚本的概要信息列表（含步骤数量）"""
        合法字段 = {"s.脚本标识", "s.脚本名称", "s.创建时间", "s.修改时间"}
        合法方向 = {"ASC", "DESC"}
        排序字段映射 = {
            "脚本标识": "s.脚本标识",
            "脚本名称": "s.脚本名称",
            "创建时间": "s.创建时间",
            "修改时间": "s.修改时间",
        }
        实际排序字段 = 排序字段映射.get(排序字段, "s.修改时间")
        if 排序方向.upper() not in 合法方向:
            排序方向 = "DESC"
        行列表 = self.连接.execute(f"""
            SELECT s.脚本标识, s.脚本名称, s.脚本描述, s.创建时间, s.修改时间,
                   COUNT(p.步骤标识) as 步骤数量
            FROM 脚本表 s
            LEFT JOIN 操作步骤表 p ON s.脚本标识 = p.所属脚本标识
            GROUP BY s.脚本标识
            ORDER BY {实际排序字段} {排序方向}
        """).fetchall()
        return [
            脚本概要信息(
                脚本标识=行[0],
                脚本名称=行[1],
                脚本描述=行[2] or "",
                创建时间=行[3],
                修改时间=行[4],
                步骤数量=行[5],
            )
            for 行 in 行列表
        ]

    def 查询启用定时的脚本(self) -> list[脚本表数据]:
        """查询所有启用定时任务的脚本"""
        行列表 = self.连接.execute(
            "SELECT * FROM 脚本表 WHERE 定时启用 = 1 ORDER BY 脚本标识 ASC"
        ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 更新定时配置(self, 脚本标识: int, 触发类型: str | None, 触发时间: str | None,
                     循环间隔: int | None, 每日时间: str | None, 启用: bool) -> None:
        """更新脚本的定时任务配置"""
        self.连接.execute(
            """UPDATE 脚本表 SET 定时触发类型 = ?, 定时触发时间 = ?, 定时循环间隔 = ?,
            定时每日时间 = ?, 定时启用 = ?, 修改时间 = ? WHERE 脚本标识 = ?""",
            (触发类型, 触发时间, 循环间隔, 每日时间, 1 if 启用 else 0,
             __import__('datetime').datetime.now().isoformat(), 脚本标识),
        )
        self.连接.commit()

    def 清除定时配置(self, 脚本标识: int) -> None:
        """清除脚本的定时任务配置"""
        self.连接.execute(
            """UPDATE 脚本表 SET 定时触发类型 = NULL, 定时触发时间 = NULL, 定时循环间隔 = NULL,
            定时每日时间 = NULL, 定时启用 = 0, 修改时间 = ? WHERE 脚本标识 = ?""",
            (__import__('datetime').datetime.now().isoformat(), 脚本标识),
        )
        self.连接.commit()

    def _行转数据(self, 行: sqlite3.Row) -> 脚本表数据:
        """将数据库行转换为脚本表数据"""
        return 脚本表数据(
            脚本标识=行["脚本标识"],
            脚本名称=行["脚本名称"],
            脚本描述=行["脚本描述"] or "",
            创建时间=行["创建时间"],
            修改时间=行["修改时间"],
            定时触发类型=行["定时触发类型"] if "定时触发类型" in 行.keys() else None,
            定时触发时间=行["定时触发时间"] if "定时触发时间" in 行.keys() else None,
            定时循环间隔=行["定时循环间隔"] if "定时循环间隔" in 行.keys() else None,
            定时每日时间=行["定时每日时间"] if "定时每日时间" in 行.keys() else None,
            定时启用=bool(行["定时启用"]) if "定时启用" in 行.keys() else False,
        )