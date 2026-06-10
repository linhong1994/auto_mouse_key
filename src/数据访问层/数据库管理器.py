import sqlite3
import os
import shutil
from datetime import datetime
from src.公共.异常定义 import 数据库损坏异常, 数据库迁移失败异常
from src.公共.日志管理 import 获取日志管理器


class 数据库管理器类:
    """sqlite3数据库管理器，负责连接、初始化、迁移"""

    def __init__(self):
        self.连接: sqlite3.Connection | None = None
        self.日志 = 获取日志管理器("数据库管理器")

    def 初始化数据库(self, 数据库路径: str | None = None) -> None:
        """连接数据库，校验schema版本，必要时执行迁移

        参数:
            数据库路径: 数据库文件路径，为None时使用默认路径
        """
        if 数据库路径 is None:
            数据目录 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
            os.makedirs(数据目录, exist_ok=True)
            数据库路径 = os.path.join(数据目录, "auto_mouse_key.db")

        self.数据库路径 = 数据库路径
        self.备份数据库()

        try:
            self.连接 = sqlite3.connect(数据库路径)
            self.连接.execute("PRAGMA foreign_keys = ON")
            self.连接.execute("PRAGMA journal_mode = WAL")
            self.连接.row_factory = sqlite3.Row
            self._执行初始化SQL()
            self.日志.info("数据库初始化完成")
        except sqlite3.Error as 异常:
            self.日志.error(f"数据库初始化失败: {异常}")
            raise 数据库损坏异常(f"数据库初始化失败: {异常}", 异常)

    def 获取连接(self) -> sqlite3.Connection:
        """获取数据库连接实例"""
        if self.连接 is None:
            raise 数据库损坏异常("数据库连接未初始化")
        return self.连接

    def 关闭连接(self) -> None:
        """关闭数据库连接"""
        if self.连接 is not None:
            self.连接.close()
            self.连接 = None
            self.日志.info("数据库连接已关闭")

    def 备份数据库(self, 备份路径: str | None = None) -> None:
        """备份数据库文件

        参数:
            备份路径: 备份文件路径，为None时自动生成
        """
        if not hasattr(self, "数据库路径") or not os.path.exists(self.数据库路径):
            return
        if 备份路径 is None:
            备份目录 = os.path.join(os.path.dirname(self.数据库路径), "backups")
            os.makedirs(备份目录, exist_ok=True)
            时间戳 = datetime.now().strftime("%Y%m%d_%H%M%S")
            备份路径 = os.path.join(备份目录, f"auto_mouse_key_{时间戳}.db")
        try:
            shutil.copy2(self.数据库路径, 备份路径)
            self.日志.info(f"数据库备份完成: {备份路径}")
        except Exception as 异常:
            self.日志.warning(f"数据库备份失败: {异常}")

    def 校验完整性(self) -> bool:
        """校验数据库文件完整性"""
        if self.连接 is None:
            return False
        try:
            结果 = self.连接.execute("PRAGMA integrity_check").fetchone()
            完整 = 结果[0] == "ok"
            if not 完整:
                self.日志.error("数据库完整性校验失败")
            return 完整
        except sqlite3.Error as 异常:
            self.日志.error(f"完整性校验异常: {异常}")
            return False

    def _执行初始化SQL(self) -> None:
        """执行数据库初始化SQL，创建所有表和索引"""
        连接 = self.获取连接()
        初始化SQL = """
        CREATE TABLE IF NOT EXISTS Schema版本表 (
            版本标识 INTEGER PRIMARY KEY CHECK (版本标识 = 1),
            版本号 INTEGER NOT NULL,
            更新时间 TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS 脚本表 (
            脚本标识 INTEGER PRIMARY KEY AUTOINCREMENT,
            脚本名称 TEXT UNIQUE NOT NULL CHECK (length(脚本名称) <= 100),
            脚本描述 TEXT CHECK (脚本描述 IS NULL OR length(脚本描述) <= 500),
            创建时间 TEXT NOT NULL,
            修改时间 TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_脚本_名称 ON 脚本表(脚本名称);
        CREATE INDEX IF NOT EXISTS idx_脚本_修改时间 ON 脚本表(修改时间);

        CREATE TABLE IF NOT EXISTS 操作步骤表 (
            步骤标识 INTEGER PRIMARY KEY AUTOINCREMENT,
            所属脚本标识 INTEGER NOT NULL,
            操作类型 TEXT NOT NULL,
            排序序号 INTEGER NOT NULL CHECK (排序序号 >= 1 AND 排序序号 <= 10000),
            目标坐标X INTEGER,
            目标坐标Y INTEGER,
            按键值 TEXT,
            修饰键列表 TEXT,
            输入文本 TEXT CHECK (输入文本 IS NULL OR length(输入文本) <= 10000),
            步骤延时 INTEGER DEFAULT 0 CHECK (步骤延时 >= 0 AND 步骤延时 <= 60000),
            滚轮量 INTEGER CHECK (滚轮量 IS NULL OR (滚轮量 >= 1 AND 滚轮量 <= 100)),
            按键保持时长 INTEGER CHECK (按键保持时长 IS NULL OR (按键保持时长 >= 100 AND 按键保持时长 <= 60000)),
            延时时长 INTEGER CHECK (延时时长 IS NULL OR (延时时长 >= 0 AND 延时时长 <= 60000)),
            起点坐标X INTEGER,
            起点坐标Y INTEGER,
            终点坐标X INTEGER,
            终点坐标Y INTEGER,
            OCR区域左上角X INTEGER,
            OCR区域左上角Y INTEGER,
            OCR区域右下角X INTEGER,
            OCR区域右下角Y INTEGER,
            OCR识别语言 TEXT,
            OCR结果变量名 TEXT,
            OCR条件类型 TEXT,
            OCR目标文本 TEXT,
            OCR逻辑关系 TEXT,
            OCR超时时间 INTEGER,
            OCR轮询间隔 INTEGER CHECK (OCR轮询间隔 IS NULL OR OCR轮询间隔 >= 200),
            OCR超时处理 TEXT,
            FOREIGN KEY (所属脚本标识) REFERENCES 脚本表(脚本标识) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_步骤_脚本排序 ON 操作步骤表(所属脚本标识, 排序序号);
        CREATE INDEX IF NOT EXISTS idx_步骤_脚本 ON 操作步骤表(所属脚本标识);

        CREATE TABLE IF NOT EXISTS 定时任务表 (
            任务标识 INTEGER PRIMARY KEY AUTOINCREMENT,
            任务名称 TEXT NOT NULL CHECK (length(任务名称) <= 100),
            关联脚本标识 INTEGER NOT NULL,
            触发类型 TEXT NOT NULL CHECK (触发类型 IN ('单次执行', '循环间隔', '每日定时')),
            触发时间 TEXT,
            循环间隔 INTEGER CHECK (循环间隔 IS NULL OR (循环间隔 >= 1 AND 循环间隔 <= 1440)),
            每日时间 TEXT,
            启用状态 INTEGER DEFAULT 1 CHECK (启用状态 IN (0, 1)),
            任务状态 TEXT DEFAULT '待执行' CHECK (任务状态 IN ('待执行', '执行中', '已完成', '已禁用')),
            FOREIGN KEY (关联脚本标识) REFERENCES 脚本表(脚本标识) ON DELETE SET NULL
        );
        CREATE INDEX IF NOT EXISTS idx_定时_脚本 ON 定时任务表(关联脚本标识);
        CREATE INDEX IF NOT EXISTS idx_定时_启用状态 ON 定时任务表(启用状态);

        CREATE TABLE IF NOT EXISTS 热键配置表 (
            配置标识 INTEGER PRIMARY KEY AUTOINCREMENT,
            功能名称 TEXT UNIQUE NOT NULL,
            热键组合 TEXT NOT NULL,
            全局生效 INTEGER DEFAULT 1 CHECK (全局生效 = 1)
        );

        CREATE TABLE IF NOT EXISTS 应用配置表 (
            配置标识 INTEGER PRIMARY KEY AUTOINCREMENT,
            配置键名 TEXT UNIQUE NOT NULL,
            配置键值 TEXT NOT NULL
        );

        INSERT OR IGNORE INTO Schema版本表 (版本标识, 版本号, 更新时间) VALUES (1, 1, '2026-06-10T00:00:00');
        """
        连接.executescript(初始化SQL)
        self._初始化预置配置(连接)
        self._初始化默认热键(连接)
        连接.commit()

    def _初始化预置配置(self, 连接: sqlite3.Connection) -> None:
        """初始化预置配置项"""
        预置配置 = {
            "悬浮窗启用": "false",
            "悬浮窗展开": "true",
            "悬浮窗位置X": "-1",
            "悬浮窗位置Y": "-1",
            "悬浮窗透明度": "100",
            "悬浮窗自动避让": "false",
            "悬浮窗日志上限": "200",
            "悬浮窗预览条数": "5",
            "OCR置信度阈值": "30",
            "数据库Schema版本": "1",
        }
        for 键名, 键值 in 预置配置.items():
            连接.execute(
                "INSERT OR IGNORE INTO 应用配置表 (配置键名, 配置键值) VALUES (?, ?)",
                (键名, 键值),
            )

    def _初始化默认热键(self, 连接: sqlite3.Connection) -> None:
        """初始化默认热键配置"""
        默认热键 = [
            ("启动录制", "<f9>"),
            ("停止录制", "<f9>"),
            ("启动回放", "<f10>"),
            ("停止回放", "<f10>"),
            ("紧急停止", "<esc>"),
        ]
        for 功能名称, 热键组合 in 默认热键:
            连接.execute(
                "INSERT OR IGNORE INTO 热键配置表 (功能名称, 热键组合) VALUES (?, ?)",
                (功能名称, 热键组合),
            )