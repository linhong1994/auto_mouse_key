import sqlite3
from src.公共.数据结构 import 操作步骤数据
from src.公共.日志管理 import 获取日志管理器


class 步骤DAO类:
    """操作步骤数据访问对象"""

    def __init__(self, 数据库连接: sqlite3.Connection):
        self.连接 = 数据库连接
        self.日志 = 获取日志管理器("步骤DAO")

    def 插入(self, 数据: 操作步骤数据) -> int:
        """插入操作步骤记录，返回步骤标识"""
        游标 = self.连接.execute(
            """INSERT INTO 操作步骤表
            (所属脚本标识, 操作类型, 步骤名称, 排序序号, 目标坐标X, 目标坐标Y, 按键值, 修饰键列表,
             输入文本, 步骤延时, 滚轮量, 按键保持时长, 延时时长, 起点坐标X, 起点坐标Y,
             终点坐标X, 终点坐标Y, OCR区域左上角X, OCR区域左上角Y, OCR区域右下角X,
             OCR区域右下角Y, OCR识别语言, OCR条件类型, OCR目标文本,
             OCR逻辑关系, OCR超时时间, OCR轮询间隔, OCR超时处理, 父步骤标识, 分支类型, 引用脚本标识)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            self._数据转元组(数据),
        )
        self.连接.commit()
        return 游标.lastrowid

    def 批量插入(self, 数据列表: list[操作步骤数据]) -> None:
        """批量插入操作步骤记录"""
        元组列表 = [self._数据转元组(数据) for 数据 in 数据列表]
        self.连接.executemany(
            """INSERT INTO 操作步骤表
            (所属脚本标识, 操作类型, 步骤名称, 排序序号, 目标坐标X, 目标坐标Y, 按键值, 修饰键列表,
             输入文本, 步骤延时, 滚轮量, 按键保持时长, 延时时长, 起点坐标X, 起点坐标Y,
             终点坐标X, 终点坐标Y, OCR区域左上角X, OCR区域左上角Y, OCR区域右下角X,
             OCR区域右下角Y, OCR识别语言, OCR条件类型, OCR目标文本,
             OCR逻辑关系, OCR超时时间, OCR轮询间隔, OCR超时处理, 父步骤标识, 分支类型, 引用脚本标识)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            元组列表,
        )
        self.连接.commit()

    def 查询By脚本(self, 脚本标识: int) -> list[操作步骤数据]:
        """查询指定脚本的顶层操作步骤（父步骤标识为空），按排序序号排列"""
        行列表 = self.连接.execute(
            "SELECT * FROM 操作步骤表 WHERE 所属脚本标识 = ? AND 父步骤标识 IS NULL ORDER BY 排序序号 ASC",
            (脚本标识,),
        ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 查询By脚本全部(self, 脚本标识: int) -> list[操作步骤数据]:
        """查询指定脚本的所有步骤（含子步骤），按排序序号排列"""
        行列表 = self.连接.execute(
            "SELECT * FROM 操作步骤表 WHERE 所属脚本标识 = ? ORDER BY 排序序号 ASC",
            (脚本标识,),
        ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 查询子步骤(self, 父步骤标识: int, 分支类型: str | None = None) -> list[操作步骤数据]:
        """查询指定父步骤的子步骤，可按分支类型过滤，按排序序号排列"""
        if 分支类型 is not None:
            行列表 = self.连接.execute(
                "SELECT * FROM 操作步骤表 WHERE 父步骤标识 = ? AND 分支类型 = ? ORDER BY 排序序号 ASC",
                (父步骤标识, 分支类型),
            ).fetchall()
        else:
            行列表 = self.连接.execute(
                "SELECT * FROM 操作步骤表 WHERE 父步骤标识 = ? ORDER BY 排序序号 ASC",
                (父步骤标识,),
            ).fetchall()
        return [self._行转数据(行) for 行 in 行列表]

    def 查询ById(self, 标识: int) -> 操作步骤数据 | None:
        """根据步骤标识查询操作步骤"""
        行 = self.连接.execute("SELECT * FROM 操作步骤表 WHERE 步骤标识 = ?", (标识,)).fetchone()
        if 行 is None:
            return None
        return self._行转数据(行)

    def 更新(self, 标识: int, 数据: 操作步骤数据) -> None:
        """更新操作步骤"""
        self.连接.execute(
            """UPDATE 操作步骤表 SET
            所属脚本标识 = ?, 操作类型 = ?, 步骤名称 = ?, 排序序号 = ?, 目标坐标X = ?, 目标坐标Y = ?,
            按键值 = ?, 修饰键列表 = ?, 输入文本 = ?, 步骤延时 = ?, 滚轮量 = ?,
            按键保持时长 = ?, 延时时长 = ?, 起点坐标X = ?, 起点坐标Y = ?, 终点坐标X = ?,
            终点坐标Y = ?, OCR区域左上角X = ?, OCR区域左上角Y = ?, OCR区域右下角X = ?,
            OCR区域右下角Y = ?, OCR识别语言 = ?, OCR条件类型 = ?,
            OCR目标文本 = ?, OCR逻辑关系 = ?, OCR超时时间 = ?, OCR轮询间隔 = ?, OCR超时处理 = ?,
            父步骤标识 = ?, 分支类型 = ?, 引用脚本标识 = ?
            WHERE 步骤标识 = ?""",
            self._数据转元组(数据, 含标识=True),
        )
        self.连接.commit()

    def 删除(self, 标识: int) -> None:
        """删除操作步骤（ON DELETE CASCADE会自动删除子步骤）"""
        self.连接.execute("DELETE FROM 操作步骤表 WHERE 步骤标识 = ?", (标识,))
        self.连接.commit()

    def 按脚本删除全部(self, 脚本标识: int) -> None:
        """删除指定脚本的所有操作步骤"""
        self.连接.execute("DELETE FROM 操作步骤表 WHERE 所属脚本标识 = ?", (脚本标识,))
        self.连接.commit()

    def 批量更新排序(self, 排序映射: dict[int, int]) -> None:
        """批量更新步骤排序序号，使用事务保证原子性

        参数:
            排序映射: {步骤标识: 新排序序号}
        """
        try:
            for 步骤标识, 新序号 in 排序映射.items():
                self.连接.execute(
                    "UPDATE 操作步骤表 SET 排序序号 = ? WHERE 步骤标识 = ?",
                    (新序号, 步骤标识),
                )
            self.连接.commit()
        except Exception:
            self.连接.rollback()
            raise

    def _数据转元组(self, 数据: 操作步骤数据, 含标识: bool = False) -> tuple:
        """将操作步骤数据转换为SQL参数元组"""
        基础元组 = (
            数据.所属脚本标识, 数据.操作类型, 数据.步骤名称, 数据.排序序号,
            数据.目标坐标X, 数据.目标坐标Y, 数据.按键值, 数据.修饰键列表,
            数据.输入文本, 数据.步骤延时, 数据.滚轮量, 数据.按键保持时长,
            数据.延时时长, 数据.起点坐标X, 数据.起点坐标Y, 数据.终点坐标X,
            数据.终点坐标Y, 数据.OCR区域左上角X, 数据.OCR区域左上角Y,
            数据.OCR区域右下角X, 数据.OCR区域右下角Y, 数据.OCR识别语言,
            数据.OCR条件类型, 数据.OCR目标文本,
            数据.OCR逻辑关系, 数据.OCR超时时间, 数据.OCR轮询间隔, 数据.OCR超时处理,
            数据.父步骤标识, 数据.分支类型, 数据.引用脚本标识,
        )
        if 含标识:
            return 基础元组 + (数据.步骤标识,)
        return 基础元组

    def _行转数据(self, 行: sqlite3.Row) -> 操作步骤数据:
        """将数据库行转换为操作步骤数据"""
        # 安全获取可能不存在的列（兼容旧数据库）
        def _安全获取(列名, 默认值=None):
            try:
                return 行[列名]
            except (IndexError, KeyError):
                return 默认值

        return 操作步骤数据(
            步骤标识=行["步骤标识"],
            所属脚本标识=行["所属脚本标识"],
            操作类型=行["操作类型"],
            步骤名称=_安全获取("步骤名称"),
            排序序号=行["排序序号"],
            目标坐标X=行["目标坐标X"],
            目标坐标Y=行["目标坐标Y"],
            按键值=行["按键值"],
            修饰键列表=行["修饰键列表"],
            输入文本=行["输入文本"],
            步骤延时=行["步骤延时"] or 0,
            滚轮量=行["滚轮量"],
            按键保持时长=行["按键保持时长"],
            延时时长=行["延时时长"],
            起点坐标X=行["起点坐标X"],
            起点坐标Y=行["起点坐标Y"],
            终点坐标X=行["终点坐标X"],
            终点坐标Y=行["终点坐标Y"],
            OCR区域左上角X=行["OCR区域左上角X"],
            OCR区域左上角Y=行["OCR区域左上角Y"],
            OCR区域右下角X=行["OCR区域右下角X"],
            OCR区域右下角Y=行["OCR区域右下角Y"],
            OCR识别语言=行["OCR识别语言"],
            OCR条件类型=_安全获取("OCR条件类型"),
            OCR目标文本=_安全获取("OCR目标文本"),
            OCR逻辑关系=_安全获取("OCR逻辑关系"),
            OCR超时时间=_安全获取("OCR超时时间"),
            OCR轮询间隔=_安全获取("OCR轮询间隔"),
            OCR超时处理=_安全获取("OCR超时处理"),
            父步骤标识=_安全获取("父步骤标识"),
            分支类型=_安全获取("分支类型"),
            引用脚本标识=_安全获取("引用脚本标识"),
        )
