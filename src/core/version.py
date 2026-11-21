"""版本与更新服务器配置。

发新版本时：提升 APP_VERSION / VERSION_CODE，重建绿色版更新包，
上传服务器并更新 version.json 即可。主程序内置的检查更新会自动发现。
"""
APP_NAME = "MC模组编辑器"
APP_VERSION = "1.0"
VERSION_CODE = 100

UPDATE_BASE = "http://47.95.246.166/mcmodeditor"
VERSION_URL = UPDATE_BASE + "/version.json"
