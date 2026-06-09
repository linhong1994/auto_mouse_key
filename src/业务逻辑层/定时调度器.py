from src.公共.数据结构 import 定时任务数据
from src.公共.枚举定义 import 定时触发类型枚举
from src.公共.日志管理 import 获取日志管理器


class 定时调度器类:
    """定时任务调度器"""

    def __init__(self, 定时任务DAO=None, 执行引擎=None):
        self.定时任务DAO = 定时任务DAO
        self.执行引擎 = 执行引擎
        self.调度器 = None
        self.日志 = 获取日志管理器("定时调度器")

    def 启动调度器(self) -> None:
        """启动调度器，从数据库加载所有启用任务"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            self.调度器 = BackgroundScheduler()
            if self.定时任务DAO:
                启用任务 = self.定时任务DAO.查询启用的任务()
                for 任务 in 启用任务:
                    self._注册任务(任务)
            self.调度器.start()
            self.日志.info("定时调度器已启动")
        except Exception as 异常:
            self.日志.error(f"定时调度器启动失败: {异常}")

    def 停止调度器(self) -> None:
        """停止调度器"""
        if self.调度器:
            self.调度器.shutdown(wait=False)
            self.调度器 = None
            self.日志.info("定时调度器已停止")

    def 创建任务(self, 任务数据: 定时任务数据) -> int:
        """创建定时任务"""
        任务标识 = self.定时任务DAO.插入(任务数据)
        if 任务数据.启用状态:
            任务数据.任务标识 = 任务标识
            self._注册任务(任务数据)
        return 任务标识

    def 修改任务(self, 任务标识: int, 任务数据: 定时任务数据) -> None:
        """修改定时任务配置"""
        self.定时任务DAO.更新(任务标识, 任务数据)
        self._注销任务(任务标识)
        if 任务数据.启用状态:
            任务数据.任务标识 = 任务标识
            self._注册任务(任务数据)

    def 启用任务(self, 任务标识: int) -> None:
        """启用定时任务"""
        任务列表 = self.定时任务DAO.查询所有()
        for 任务 in 任务列表:
            if 任务.任务标识 == 任务标识:
                任务.启用状态 = True
                任务.任务状态 = "待执行"
                self.定时任务DAO.更新(任务标识, 任务)
                self._注册任务(任务)
                break

    def 禁用任务(self, 任务标识: int) -> None:
        """禁用定时任务"""
        任务列表 = self.定时任务DAO.查询所有()
        for 任务 in 任务列表:
            if 任务.任务标识 == 任务标识:
                任务.启用状态 = False
                任务.任务状态 = "已禁用"
                self.定时任务DAO.更新(任务标识, 任务)
                self._注销任务(任务标识)
                break

    def 删除任务(self, 任务标识: int) -> None:
        """删除定时任务"""
        self._注销任务(任务标识)
        self.定时任务DAO.删除(任务标识)

    def 查询所有任务(self) -> list[定时任务数据]:
        """查询所有定时任务"""
        return self.定时任务DAO.查询所有()

    def _注册任务(self, 任务: 定时任务数据) -> None:
        """注册定时任务到调度器"""
        if not self.调度器 or not self.执行引擎:
            return
        try:
            任务标识 = str(任务.任务标识)
            if 任务.触发类型 == "单次执行" and 任务.触发时间:
                from datetime import datetime
                运行时间 = datetime.fromisoformat(任务.触发时间)
                self.调度器.add_job(
                    self._触发任务,
                    "date",
                    run_date=运行时间,
                    args=[任务.任务标识, 任务.关联脚本标识],
                    id=任务标识,
                    replace_existing=True,
                )
            elif 任务.触发类型 == "循环间隔" and 任务.循环间隔:
                self.调度器.add_job(
                    self._触发任务,
                    "interval",
                    minutes=任务.循环间隔,
                    args=[任务.任务标识, 任务.关联脚本标识],
                    id=任务标识,
                    replace_existing=True,
                )
            elif 任务.触发类型 == "每日定时" and 任务.每日时间:
                时, 分 = map(int, 任务.每日时间.split(":"))
                self.调度器.add_job(
                    self._触发任务,
                    "cron",
                    hour=时,
                    minute=分,
                    args=[任务.任务标识, 任务.关联脚本标识],
                    id=任务标识,
                    replace_existing=True,
                )
        except Exception as 异常:
            self.日志.error(f"注册定时任务{任务.任务标识}失败: {异常}")

    def _注销任务(self, 任务标识: int) -> None:
        """从调度器注销定时任务"""
        if not self.调度器:
            return
        try:
            self.调度器.remove_job(str(任务标识))
        except Exception:
            pass

    def _触发任务(self, 任务标识: int, 脚本标识: int) -> None:
        """触发定时任务执行"""
        self.日志.info(f"定时任务{任务标识}触发，执行脚本{脚本标识}")
        if self.执行引擎:
            self.执行引擎.执行脚本(脚本标识)