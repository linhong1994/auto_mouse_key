from PySide6.QtCore import QObject, Signal
from src.公共.日志管理 import 获取日志管理器


class 定时调度器类(QObject):
    """定时任务调度器，基于脚本表的定时配置"""

    定时激活信号 = Signal(int)    # 定时任务激活时发射，参数为脚本标识
    定时停止信号 = Signal()        # 定时任务停止时发射

    def __init__(self, 脚本DAO=None, 执行引擎=None):
        super().__init__()
        self.脚本DAO = 脚本DAO
        self.执行引擎 = 执行引擎
        self.调度器 = None
        self.当前活动脚本标识: int = 0
        self.日志 = 获取日志管理器("定时调度器")

    def 启动调度器(self) -> None:
        """启动调度器，从数据库加载所有启用定时的脚本"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            self.调度器 = BackgroundScheduler()
            if self.脚本DAO:
                启用脚本 = self.脚本DAO.查询启用定时的脚本()
                for 脚本 in 启用脚本:
                    self._注册任务(脚本)
                if 启用脚本:
                    self.当前活动脚本标识 = 启用脚本[0].脚本标识
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

    def 创建任务(self, 脚本标识: int, 触发类型: str, 触发时间: str | None = None,
                 循环间隔: int | None = None, 每日时间: str | None = None, 启用: bool = True) -> None:
        """为脚本设置定时任务（全局单任务，设置前先清除旧任务）"""
        if self.当前活动脚本标识:
            self.停止活动任务()
        self.脚本DAO.更新定时配置(脚本标识, 触发类型, 触发时间, 循环间隔, 每日时间, 启用)
        if 启用:
            脚本 = self.脚本DAO.查询ById(脚本标识)
            if 脚本:
                self._注册任务(脚本)
                self.当前活动脚本标识 = 脚本标识
                self.定时激活信号.emit(脚本标识)

    def 停止活动任务(self) -> None:
        """停止当前活动的定时任务"""
        if self.当前活动脚本标识:
            self._注销任务()
            self.脚本DAO.清除定时配置(self.当前活动脚本标识)
            self.当前活动脚本标识 = 0
            self.定时停止信号.emit()
            if self.执行引擎:
                self.执行引擎.定时任务激活 = False

    def 是否有活动任务(self) -> bool:
        """判断当前是否有活动的定时任务"""
        return self.当前活动脚本标识 != 0

    def 获取活动任务脚本标识(self) -> int:
        """获取活动定时任务关联的脚本标识，无活动任务时返回0"""
        return self.当前活动脚本标识

    def _注册任务(self, 脚本) -> None:
        """注册定时任务到调度器"""
        if not self.调度器 or not self.执行引擎:
            return
        try:
            if not 脚本.定时触发类型:
                return
            任务标识 = str(脚本.脚本标识)
            if 脚本.定时触发类型 == "单次执行" and 脚本.定时触发时间:
                from datetime import datetime
                运行时间 = datetime.fromisoformat(脚本.定时触发时间)
                self.调度器.add_job(
                    self._触发任务,
                    "date",
                    run_date=运行时间,
                    args=[脚本.脚本标识],
                    id=任务标识,
                    replace_existing=True,
                )
            elif 脚本.定时触发类型 == "循环间隔" and 脚本.定时循环间隔:
                self.调度器.add_job(
                    self._触发任务,
                    "interval",
                    minutes=脚本.定时循环间隔,
                    args=[脚本.脚本标识],
                    id=任务标识,
                    replace_existing=True,
                )
            elif 脚本.定时触发类型 == "每日定时" and 脚本.定时每日时间:
                时, 分 = map(int, 脚本.定时每日时间.split(":"))
                self.调度器.add_job(
                    self._触发任务,
                    "cron",
                    hour=时,
                    minute=分,
                    args=[脚本.脚本标识],
                    id=任务标识,
                    replace_existing=True,
                )
        except Exception as 异常:
            self.日志.error(f"注册脚本{脚本.脚本标识}定时任务失败: {异常}")

    def _注销任务(self) -> None:
        """从调度器注销当前活动任务"""
        if not self.调度器 or not self.当前活动脚本标识:
            return
        try:
            self.调度器.remove_job(str(self.当前活动脚本标识))
        except Exception:
            pass

    def _触发任务(self, 脚本标识: int) -> None:
        """触发定时任务执行"""
        self.日志.info(f"定时任务触发，执行脚本{脚本标识}")
        if self.执行引擎:
            self.执行引擎.定时任务激活 = True
            self.执行引擎.执行脚本(脚本标识)
