import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from src.数据访问层.数据库管理器 import 数据库管理器类
from src.数据访问层.脚本DAO import 脚本DAO类
from src.数据访问层.步骤DAO import 步骤DAO类
from src.数据访问层.定时任务DAO import 定时任务DAO类
from src.数据访问层.热键DAO import 热键DAO类
from src.数据访问层.配置DAO import 配置DAO类
from src.数据访问层.JSON序列化器 import JSON序列化器类
from src.业务逻辑层.鼠标操作执行器 import 鼠标操作执行器类
from src.业务逻辑层.按键操作执行器 import 按键操作执行器类
from src.业务逻辑层.OCR识别服务 import OCR识别服务类
from src.业务逻辑层.OCR条件判断器 import OCR条件判断器类
from src.业务逻辑层.录制控制器 import 录制控制器类
from src.业务逻辑层.回放控制器 import 回放控制器类
from src.业务逻辑层.执行引擎 import 执行引擎类
from src.业务逻辑层.脚本管理服务 import 脚本管理服务类
from src.业务逻辑层.步骤管理服务 import 步骤管理服务类
from src.业务逻辑层.定时调度器 import 定时调度器类
from src.业务逻辑层.热键管理器 import 热键管理器类
from src.表现层.主窗口 import 主窗口类
from src.表现层.脚本列表组件 import 脚本列表组件类
from src.表现层.操作列表组件 import 操作列表组件类
from src.表现层.步骤详情组件 import 步骤详情组件类

from src.表现层.执行控制组件 import 执行控制组件类
from src.表现层.状态信息组件 import 状态信息组件类
from src.表现层.悬浮窗 import 悬浮窗类
from src.表现层.系统托盘 import 系统托盘类
from src.公共.枚举定义 import 运行状态枚举
from src.公共.日志管理 import 获取日志管理器


def 初始化数据访问层():
    """初始化数据访问层，返回各组件实例"""
    数据库管理器 = 数据库管理器类()
    数据库管理器.初始化数据库()
    连接 = 数据库管理器.获取连接()

    脚本DAO = 脚本DAO类(连接)
    步骤DAO = 步骤DAO类(连接)
    定时任务DAO = 定时任务DAO类(连接)
    热键DAO = 热键DAO类(连接)
    配置DAO = 配置DAO类(连接)
    JSON序列化器 = JSON序列化器类()

    return 数据库管理器, 脚本DAO, 步骤DAO, 定时任务DAO, 热键DAO, 配置DAO, JSON序列化器


def 初始化业务逻辑层(脚本DAO, 步骤DAO, 定时任务DAO, 热键DAO, 配置DAO, JSON序列化器):
    """初始化业务逻辑层，返回各组件实例"""
    鼠标执行器 = 鼠标操作执行器类()
    按键执行器 = 按键操作执行器类()
    OCR服务 = OCR识别服务类(配置DAO)
    OCR条件判断器 = OCR条件判断器类(OCR服务)

    脚本管理服务 = 脚本管理服务类(脚本DAO, 步骤DAO, JSON序列化器, 定时任务DAO)
    步骤管理服务 = 步骤管理服务类(步骤DAO)

    回放控制器 = 回放控制器类(鼠标执行器, 按键执行器, OCR服务, OCR条件判断器)
    执行引擎 = 执行引擎类(回放控制器, 脚本管理服务, 步骤管理服务)
    录制控制器 = 录制控制器类(脚本管理服务, 步骤管理服务)

    定时调度器 = 定时调度器类(定时任务DAO, 执行引擎)
    热键管理器 = 热键管理器类(热键DAO)

    return (鼠标执行器, 按键执行器, OCR服务, OCR条件判断器,
            脚本管理服务, 步骤管理服务, 回放控制器, 执行引擎,
            录制控制器, 定时调度器, 热键管理器, 配置DAO)


def 初始化表现层(执行引擎, 录制控制器, 脚本管理服务, 步骤管理服务,
                   定时调度器, 热键管理器, 配置DAO):
    """初始化表现层，返回主窗口实例"""
    主窗口 = 主窗口类()

    脚本列表组件 = 脚本列表组件类(脚本管理服务)
    操作列表组件 = 操作列表组件类(步骤管理服务)
    步骤详情组件 = 步骤详情组件类()

    执行控制组件 = 执行控制组件类()
    状态信息组件 = 状态信息组件类(执行引擎, 热键管理器)
    悬浮窗 = 悬浮窗类(执行引擎, 配置DAO)
    系统托盘 = 系统托盘类()

    主窗口.脚本列表组件 = 脚本列表组件
    主窗口.操作列表组件 = 操作列表组件
    主窗口.步骤详情组件 = 步骤详情组件

    主窗口.执行控制组件 = 执行控制组件
    主窗口.状态信息组件 = 状态信息组件
    主窗口.悬浮窗 = 悬浮窗
    主窗口.系统托盘 = 系统托盘
    主窗口.热键管理器 = 热键管理器

    return 主窗口, 悬浮窗, 系统托盘


def 连接信号槽(主窗口, 执行引擎, 录制控制器, 脚本管理服务, 步骤管理服务,
               定时调度器, 热键管理器, 配置DAO, 悬浮窗, 系统托盘):
    """连接所有组件的信号与槽"""
    脚本列表 = 主窗口.脚本列表组件
    操作列表 = 主窗口.操作列表组件

    执行控制 = 主窗口.执行控制组件
    状态信息 = 主窗口.状态信息组件

    脚本列表.脚本选中信号.connect(lambda 标识: 操作列表.加载脚本步骤(标识))

    脚本列表.脚本新建信号.connect(lambda: _新建脚本(脚本管理服务, 脚本列表))
    脚本列表.脚本删除信号.connect(lambda 标识: _删除脚本(脚本管理服务, 脚本列表, 标识))
    脚本列表.脚本复制信号.connect(lambda 标识: _复制脚本(脚本管理服务, 脚本列表, 标识))
    脚本列表.脚本编辑信号.connect(lambda 标识: _编辑脚本信息(脚本管理服务, 脚本列表, 标识))
    脚本列表.脚本导出信号.connect(lambda 标识: _导出脚本(脚本管理服务, 标识))
    脚本列表.脚本导入信号.connect(lambda: _导入脚本(脚本管理服务, 脚本列表))

    操作列表.步骤删除信号.connect(lambda 标识: _删除步骤(步骤管理服务, 操作列表, 标识))
    操作列表.步骤排序信号.connect(lambda 原, 新: _排序步骤(步骤管理服务, 操作列表, 原, 新))

    操作列表.步骤选中信号.connect(lambda 标识: _显示步骤详情(步骤管理服务, 主窗口.步骤详情组件, 标识))

    执行控制.回放信号.connect(lambda 速度, 次数: _执行回放(执行引擎, 脚本列表, 速度, 次数))
    执行控制.停止信号.connect(执行引擎.停止执行)
    执行控制.录制信号.connect(lambda: _切换录制(录制控制器, 执行控制, 脚本列表))

    执行引擎.状态变更信号.connect(lambda 状态, 进度: _更新状态(主窗口, 执行控制, 悬浮窗, 状态信息, 状态, 进度))
    执行引擎.日志信号.connect(悬浮窗.追加运行日志)
    执行引擎.步骤执行信号.connect(悬浮窗.更新即将运行操作)

    录制控制器.录制步骤捕获.connect(操作列表.追加录制步骤)
    录制控制器.录制状态变更.connect(执行控制.设置录制状态)
    录制控制器.录制状态变更.connect(lambda 录制中: 脚本列表.刷新列表() if not 录制中 else None)

    热键管理器.热键触发信号.connect(lambda 功能: _处理热键(功能, 执行引擎, 录制控制器, 执行控制, 脚本列表))

    系统托盘.显示主窗口信号.connect(主窗口.show)
    系统托盘.启动录制信号.connect(lambda: _切换录制(录制控制器, 执行控制, 脚本列表))
    系统托盘.启动回放信号.connect(lambda: _执行回放(执行引擎, 脚本列表, 1.0, 1))
    系统托盘.退出信号.connect(QApplication.instance().quit)

    悬浮窗.紧急停止信号.connect(执行引擎.停止执行)

    _连接所有菜单(主窗口, 脚本管理服务, 脚本列表, 执行引擎, 录制控制器, 执行控制,
                   定时调度器, 热键管理器, 配置DAO, 悬浮窗)


def _连接所有菜单(主窗口, 脚本管理服务, 脚本列表, 执行引擎, 录制控制器, 执行控制,
                   定时调度器, 热键管理器, 配置DAO, 悬浮窗):
    """连接菜单栏所有动作"""
    动作映射 = {}
    for 动作 in 主窗口._菜单动作:
        动作映射[动作.text()] = 动作



    动作映射.get("热键设置").triggered.connect(lambda: _显示热键设置(主窗口)) if 动作映射.get("热键设置") else None
    动作映射.get("悬浮窗设置").triggered.connect(lambda: _显示悬浮窗设置(悬浮窗, 配置DAO)) if 动作映射.get("悬浮窗设置") else None
    动作映射.get("定时任务").triggered.connect(lambda: _显示定时任务(定时调度器, 脚本管理服务)) if 动作映射.get("定时任务") else None
    动作映射.get("关于").triggered.connect(lambda: QMessageBox.about(主窗口, "关于", "自动操作工具 v1.0\n\n基于Python+PySide6的自动鼠标、按键操作工具")) if 动作映射.get("关于") else None


def _编辑脚本信息(脚本管理服务, 脚本列表, 标识):
    from PySide6.QtWidgets import QInputDialog
    脚本 = 脚本管理服务.脚本DAO.查询ById(标识)
    if 脚本:
        名称, 确定 = QInputDialog.getText(None, "编辑脚本", "脚本名称:", text=脚本.脚本名称)
        if 确定 and 名称:
            脚本管理服务.修改脚本信息(标识, 名称=名称)
            脚本列表.刷新列表()


def _导出脚本(脚本管理服务, 标识):
    from PySide6.QtWidgets import QFileDialog
    if not 标识:
        return
    路径, _ = QFileDialog.getSaveFileName(None, "导出脚本", "", "JSON文件 (*.json)")
    if 路径:
        脚本管理服务.导出为JSON(标识, 路径)


def _导入脚本(脚本管理服务, 脚本列表):
    from PySide6.QtWidgets import QFileDialog
    路径, _ = QFileDialog.getOpenFileName(None, "导入脚本", "", "JSON文件 (*.json)")
    if 路径:
        try:
            脚本管理服务.从JSON导入(路径)
            脚本列表.刷新列表()
        except Exception as 异常:
            QMessageBox.warning(None, "导入失败", str(异常))


def _显示定时任务(定时调度器, 脚本管理服务):
    from src.表现层.定时任务管理组件 import 定时任务管理组件类
    对话框 = 定时任务管理组件类(定时调度器, 脚本管理服务)
    对话框.setWindowTitle("定时任务管理")
    from PySide6.QtWidgets import QDialog
    对话框.exec() if hasattr(对话框, 'exec') else 对话框.show()


def _新建脚本(脚本管理服务, 脚本列表):
    from PySide6.QtWidgets import QInputDialog
    名称, 确定 = QInputDialog.getText(None, "新建脚本", "脚本名称:")
    if 确定 and 名称:
        脚本管理服务.创建脚本(名称)
        脚本列表.刷新列表()


def _删除脚本(脚本管理服务, 脚本列表, 标识):
    脚本管理服务.删除脚本(标识)
    脚本列表.刷新列表()


def _复制脚本(脚本管理服务, 脚本列表, 标识):
    脚本管理服务.复制脚本(标识)
    脚本列表.刷新列表()


def _添加步骤(步骤管理服务, 操作列表, 类型):
    from src.公共.数据结构 import 操作步骤数据
    脚本标识 = 操作列表.当前脚本标识
    if 脚本标识:
        步骤 = 操作步骤数据(操作类型=类型, 所属脚本标识=脚本标识)
        步骤管理服务.添加步骤(脚本标识, 步骤)
        操作列表.加载脚本步骤(脚本标识)


def _删除步骤(步骤管理服务, 操作列表, 标识):
    步骤管理服务.删除步骤(标识)
    操作列表.加载脚本步骤(操作列表.当前脚本标识)


def _排序步骤(步骤管理服务, 操作列表, 原序号, 新序号):
    步骤管理服务.拖动排序(操作列表.当前脚本标识, 原序号, 新序号)
    操作列表.加载脚本步骤(操作列表.当前脚本标识)


def _显示步骤详情(步骤管理服务, 详情组件, 步骤标识):
    """根据步骤标识查询并显示步骤详情"""
    步骤 = 步骤管理服务.步骤DAO.查询ById(步骤标识)
    if 步骤:
        详情组件.显示步骤详情(步骤)
    else:
        详情组件.清空详情()


def _保存步骤(步骤管理服务, 操作列表, 数据):
    if 数据.步骤标识:
        步骤管理服务.修改步骤(数据.步骤标识, 数据)
    操作列表.加载脚本步骤(操作列表.当前脚本标识)


def _执行回放(执行引擎, 脚本列表, 速度, 次数):
    脚本标识 = 脚本列表.当前脚本标识
    if 脚本标识:
        执行引擎.执行脚本(脚本标识, 速度, 次数)


def _切换录制(录制控制器, 执行控制, 脚本列表):
    if 录制控制器.是否录制中():
        录制控制器.停止录制()
        脚本列表.刷新列表()
    else:
        录制控制器.启动录制()


def _更新状态(主窗口, 执行控制, 悬浮窗, 状态信息, 状态, 进度):
    try:
        运行状态 = 运行状态枚举(状态)
        主窗口.更新执行状态显示(运行状态, 进度)
        悬浮窗.更新运行状态(运行状态, 进度)
        执行控制.设置回放状态(运行状态 == 运行状态枚举.回放中)
        状态信息.更新执行状态(状态, 进度)
    except Exception:
        pass


def _处理热键(功能, 执行引擎, 录制控制器, 执行控制, 脚本列表):
    if 功能 in ("启动录制", "停止录制"):
        _切换录制(录制控制器, 执行控制, 脚本列表)
    elif 功能 in ("启动回放", "停止回放"):
        if 执行引擎.当前状态 == 运行状态枚举.回放中:
            执行引擎.停止执行()
        else:
            _执行回放(执行引擎, 脚本列表, 1.0, 1)
    elif 功能 == "紧急停止":
        执行引擎.停止执行()


def _显示悬浮窗设置(悬浮窗, 配置DAO):
    """显示悬浮窗设置对话框"""
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QSlider, QDialogButtonBox, QLabel, QHBoxLayout
    对话框 = QDialog()
    对话框.setWindowTitle("悬浮窗设置")
    布局 = QVBoxLayout(对话框)

    启用复选框 = QCheckBox("启用悬浮窗")
    当前启用 = 配置DAO.查询配置("悬浮窗启用", "false") == "true"
    启用复选框.setChecked(当前启用)
    布局.addWidget(启用复选框)

    避让复选框 = QCheckBox("自动避让（操作目标在悬浮窗区域时临时隐藏）")
    当前避让 = 配置DAO.查询配置("悬浮窗自动避让", "false") == "true"
    避让复选框.setChecked(当前避让)
    布局.addWidget(避让复选框)

    透明度布局 = QHBoxLayout()
    透明度布局.addWidget(QLabel("透明度:"))
    透明度滑块 = QSlider(Qt.Orientation.Horizontal)
    透明度滑块.setRange(20, 100)
    当前透明度 = int(配置DAO.查询配置("悬浮窗透明度", "100"))
    透明度滑块.setValue(当前透明度)
    透明度布局.addWidget(透明度滑块)
    透明度标签 = QLabel(f"{当前透明度}%")
    透明度滑块.valueChanged.connect(lambda v: 透明度标签.setText(f"{v}%"))
    透明度布局.addWidget(透明度标签)
    布局.addLayout(透明度布局)

    按钮盒 = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    按钮盒.accepted.connect(对话框.accept)
    按钮盒.rejected.connect(对话框.reject)
    布局.addWidget(按钮盒)

    if 对话框.exec() == QDialog.DialogCode.Accepted:
        配置DAO.设置配置("悬浮窗启用", "true" if 启用复选框.isChecked() else "false")
        配置DAO.设置配置("悬浮窗自动避让", "true" if 避让复选框.isChecked() else "false")
        配置DAO.设置配置("悬浮窗透明度", str(透明度滑块.value()))
        if 启用复选框.isChecked():
            悬浮窗.设置透明度(透明度滑块.value())
            悬浮窗.开启悬浮窗()
        else:
            悬浮窗.关闭悬浮窗()


def _显示热键设置(主窗口):
    """显示热键设置界面"""
    from src.表现层.热键设置组件 import 热键设置组件类
    对话框 = 热键设置组件类(主窗口.热键管理器 if hasattr(主窗口, '热键管理器') else None)
    对话框.setWindowTitle("热键设置")
    对话框.配置保存信号.connect(
        lambda: 主窗口.执行控制组件.更新热键按钮文字(主窗口.热键管理器.获取当前配置())
    )
    对话框.exec()


def main():
    """应用入口函数"""
    日志 = 获取日志管理器("主程序")
    日志.info("应用启动中...")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        (数据库管理器, 脚本DAO, 步骤DAO, 定时任务DAO,
         热键DAO, 配置DAO, JSON序列化器) = 初始化数据访问层()

        (鼠标执行器, 按键执行器, OCR服务, OCR条件判断器,
         脚本管理服务, 步骤管理服务, 回放控制器, 执行引擎,
         录制控制器, 定时调度器, 热键管理器, 配置DAO_业务层) = 初始化业务逻辑层(
            脚本DAO, 步骤DAO, 定时任务DAO, 热键DAO, 配置DAO, JSON序列化器)

        主窗口, 悬浮窗, 系统托盘 = 初始化表现层(
            执行引擎, 录制控制器, 脚本管理服务, 步骤管理服务,
            定时调度器, 热键管理器, 配置DAO)

        热键管理器.加载配置()
        定时调度器.启动调度器()

        主窗口.初始化界面()

        # 热键加载后更新按钮文字
        主窗口.执行控制组件.更新热键按钮文字(热键管理器.获取当前配置())

        回放控制器.悬浮窗 = 悬浮窗
        回放控制器.配置DAO = 配置DAO

        连接信号槽(主窗口, 执行引擎, 录制控制器, 脚本管理服务,
                   步骤管理服务, 定时调度器, 热键管理器, 配置DAO, 悬浮窗, 系统托盘)

        主窗口.脚本列表组件.刷新列表()
        主窗口.show()
        系统托盘.show()

        悬浮窗启用 = 配置DAO.查询配置("悬浮窗启用", "false") == "true"
        if 悬浮窗启用:
            悬浮窗.开启悬浮窗()


        日志.info("应用启动完成")

        退出码 = app.exec()

        热键管理器.停止()
        定时调度器.停止调度器()
        数据库管理器.关闭连接()

        日志.info("应用已退出")
        sys.exit(退出码)

    except Exception as 异常:
        日志.critical(f"应用启动失败: {异常}")
        QMessageBox.critical(None, "启动失败", f"应用启动失败:\n{异常}")
        sys.exit(1)


if __name__ == "__main__":
    main()