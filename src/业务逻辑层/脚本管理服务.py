from datetime import datetime
from src.公共.数据结构 import 脚本表数据, 脚本概要信息, 操作步骤数据
from src.公共.异常定义 import 脚本名称重复异常, 脚本名称为空异常, 脚本循环引用异常
from src.公共.日志管理 import 获取日志管理器


class 脚本管理服务类:
    """操作脚本管理服务"""

    def __init__(self, 脚本DAO=None, 步骤DAO=None, JSON序列化器=None, 定时任务DAO=None):
        self.脚本DAO = 脚本DAO
        self.步骤DAO = 步骤DAO
        self.JSON序列化器 = JSON序列化器
        self.定时任务DAO = 定时任务DAO
        self.日志 = 获取日志管理器("脚本管理服务")

    def 查询所有脚本(self, 排序字段: str = "修改时间", 排序方向: str = "降序") -> list[脚本概要信息]:
        """查询所有脚本的基本信息列表"""
        方向映射 = {"降序": "DESC", "升序": "ASC"}
        实际方向 = 方向映射.get(排序方向, "DESC")
        return self.脚本DAO.查询概要列表(排序字段, 实际方向)

    def 按名称搜索(self, 关键词: str) -> list[脚本概要信息]:
        """按脚本名称模糊搜索"""
        脚本列表 = self.脚本DAO.按名称模糊查询(关键词)
        return [
            脚本概要信息(
                脚本标识=s.脚本标识,
                脚本名称=s.脚本名称,
                脚本描述=s.脚本描述,
                创建时间=s.创建时间,
                修改时间=s.修改时间,
                步骤数量=self.脚本DAO.统计步骤数量(s.脚本标识),
            )
            for s in 脚本列表
        ]

    def 创建脚本(self, 名称: str, 描述: str = "") -> int:
        """创建新脚本，返回脚本标识"""
        if not 名称 or not 名称.strip():
            raise 脚本名称为空异常("脚本名称不能为空")
        已有 = self.脚本DAO.按名称模糊查询(名称)
        for s in 已有:
            if s.脚本名称 == 名称:
                raise 脚本名称重复异常(f"脚本名称'{名称}'已存在")
        时间戳 = datetime.now().isoformat()
        数据 = 脚本表数据(脚本名称=名称, 脚本描述=描述, 创建时间=时间戳, 修改时间=时间戳)
        return self.脚本DAO.插入(数据)

    def 修改脚本信息(self, 脚本标识: int, 名称: str | None = None, 描述: str | None = None) -> None:
        """修改脚本基本信息"""
        原数据 = self.脚本DAO.查询ById(脚本标识)
        if 原数据 is None:
            return
        if 名称 is not None:
            已有 = self.脚本DAO.按名称模糊查询(名称)
            for s in 已有:
                if s.脚本名称 == 名称 and s.脚本标识 != 脚本标识:
                    raise 脚本名称重复异常(f"脚本名称'{名称}'已存在")
            原数据.脚本名称 = 名称
        if 描述 is not None:
            原数据.脚本描述 = 描述
        原数据.修改时间 = datetime.now().isoformat()
        self.脚本DAO.更新(脚本标识, 原数据)

    def 删除脚本(self, 脚本标识: int) -> None:
        """删除脚本及关联的所有操作步骤"""
        self.脚本DAO.删除(脚本标识)

    def 复制脚本(self, 脚本标识: int) -> int:
        """复制脚本，新脚本名称带"副本"后缀"""
        原数据 = self.脚本DAO.查询ById(脚本标识)
        if 原数据 is None:
            return 0
        原步骤 = self.步骤DAO.查询By脚本(脚本标识)
        时间戳 = datetime.now().isoformat()
        新数据 = 脚本表数据(
            脚本名称=原数据.脚本名称 + "_副本",
            脚本描述=原数据.脚本描述,
            创建时间=时间戳,
            修改时间=时间戳,
        )
        新标识 = self.脚本DAO.插入(新数据)
        for 步骤 in 原步骤:
            步骤.步骤标识 = 0
            步骤.所属脚本标识 = 新标识
        if 原步骤:
            self.步骤DAO.批量插入(原步骤)
        return 新标识

    def 导出为JSON(self, 脚本标识: int, 文件路径: str) -> None:
        """将脚本导出为JSON文件"""
        脚本数据 = self.脚本DAO.查询ById(脚本标识)
        if 脚本数据 is None:
            return
        步骤列表 = self.步骤DAO.查询By脚本(脚本标识)
        JSON数据 = self.JSON序列化器.导出脚本(脚本数据, 步骤列表)
        self.JSON序列化器.写入文件(JSON数据, 文件路径)

    def 从JSON导入(self, 文件路径: str) -> int:
        """从JSON文件导入脚本到数据库"""
        JSON数据 = self.JSON序列化器.读取文件(文件路径)
        脚本数据, 步骤列表 = self.JSON序列化器.导入脚本(JSON数据)
        时间戳 = datetime.now().isoformat()
        脚本数据.创建时间 = 时间戳
        脚本数据.修改时间 = 时间戳
        脚本标识 = self.脚本DAO.插入(脚本数据)
        for 步骤 in 步骤列表:
            步骤.所属脚本标识 = 脚本标识
        if 步骤列表:
            self.步骤DAO.批量插入(步骤列表)
        return 脚本标识

    def 查询关联定时任务(self, 脚本标识: int) -> list:
        """查询引用该脚本的定时任务列表"""
        if self.定时任务DAO:
            return self.定时任务DAO.按脚本查询(脚本标识)
        return []

    def 检查循环引用(self, 当前脚本标识: int, 目标脚本标识: int) -> bool:
        """检查将目标脚本作为步骤添加到当前脚本是否会产生循环引用

        规则：
        - 不能引用自身
        - 如果目标脚本（或其任何嵌套引用脚本）引用了当前脚本，则禁止

        返回:
            True 表示会产生循环引用，False 表示安全
        """
        if 当前脚本标识 == 目标脚本标识:
            return True
        已访问 = set()
        return self._深度检查引用(目标脚本标识, 当前脚本标识, 已访问)

    def _深度检查引用(self, 检查脚本标识: int, 禁止脚本标识: int, 已访问: set) -> bool:
        """递归检查脚本引用链是否包含禁止脚本

        返回 True 表示存在循环引用
        """
        if 检查脚本标识 == 禁止脚本标识:
            return True
        if 检查脚本标识 in 已访问:
            return False
        已访问.add(检查脚本标识)
        if not self.步骤DAO:
            return False
        步骤列表 = self.步骤DAO.查询By脚本全部(检查脚本标识)
        for 步骤 in 步骤列表:
            if 步骤.操作类型 == "调用脚本" and 步骤.引用脚本标识:
                if self._深度检查引用(步骤.引用脚本标识, 禁止脚本标识, 已访问):
                    return True
        return False