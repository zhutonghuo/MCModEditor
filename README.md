# MC模组编辑器

一个用于创作《我的世界》模组的图形化桌面工坊。多文件模块化架构，PyQt5 构建，提供安装包。

## 🌐 在线资源

- **官网下载页**：http://47.95.246.166/mcmodeditor/
- **GitHub 仓库**：https://github.com/zhutonghuo/MCModEditor
- **GitHub Release（含安装包）**：https://github.com/zhutonghuo/MCModEditor/releases/tag/v1.0

## ✨ 功能

| 工坊 | 能力 |
|---|---|
| 🎲 模型工坊 | 体素方块堆砌，等距 3D 实时预览，一键生成剑/人形/立方/十字形状，导出 MC 模型 JSON |
| 🎬 动画工坊 | 关键帧时间轴，位移/旋转/缩放插值，实时播放，导出 MC 动画 JSON |
| 🖼️ 物品栏工坊 | 名称、Lore、堆叠、耐久、稀有度、发光，物品栏格子预览 |
| 🧩 积木编程 | 事件/条件/动作三类积木拖拽拼接，参数可编辑，一键生成 MC 命令 |
| ⌘ 命令工坊 | 10 类命令模板可视化拼参，命令列表管理与语法校验 |
| 🎛️ UI 工坊 | 拖拽式界面设计器（按钮/文本/输入框/面板/图片/复选框），属性编辑，导出界面 JSON |

另有：工程保存/加载（`.mcme`）、一键导出资源包/数据包/界面 JSON、明暗主题切换、全自绘矢量图标（无 emoji）、**一键自动更新**。

## 🔄 自动更新（重点）

- **程序内更新**：点工具栏/帮助菜单的「检查更新」，自动拉取服务器 `version.json`，发现新版后显示更新日志、下载并校验 SHA1，程序退出后在后台覆盖安装并自动重启。**不卸载、不删除工程文件**。
- **安装包覆盖更新**：再次运行安装包时，会自动扫描注册表/常见目录/快捷方式定位已安装目录，显著提示"检测到已安装 vX，继续将覆盖更新"，默认定位到该目录；覆盖只替换程序文件，保留你的工程。若想换目录全新安装，点「浏览」选择其他位置即可。
- 更新包：`MCModEditor-Update-v1.0.zip`（绿色版，供程序内更新下载）；服务器清单：`version.json`。

发新版流程：提升 `src/core/version.py` 的版本号 → `python build.py` → `python make_version.py`（生成 zip+清单）→ 上传服务器并更新 `version.json`。

## 📦 安装

运行 `MCModEditor-Setup-v1.0.exe`，一路下一步即可。支持：
- 开始菜单 / 桌面快捷方式
- 安装完成自动打开编辑器（可取消勾选）
- 覆盖更新（保留工程文件）

也可直接运行绿色版：进入 `dist/MC模组编辑器/`，双击 `MC模组编辑器.exe`。

## 🚀 从源码运行

```bash
pip install PyQt5 Pillow pyinstaller
cd src
python main.py
```

## 🔨 自己构建

```bash
python build.py                          # 多文件 exe → dist/
python 安装程序/make_installer.py        # 安装包 → 安装包/
python make_version.py                   # 更新包 zip + version.json
python publish.py                        # 发布到服务器 + GitHub（需环境变量）
```

## 📂 目录结构

```
MC模组编辑器/
├── src/
│   ├── main.py              # 程序入口
│   ├── core/                # 数据层：工程/模型/动画/积木/命令/导出/自动更新
│   └── ui/                  # 界面层：六大编辑器 + 主窗口 + 图标/主题
├── 安装程序/
│   ├── installer_src.py     # 安装向导源码（检测已装 + 覆盖更新）
│   └── make_installer.py    # 安装包构建脚本
├── build.py                 # PyInstaller 构建脚本
├── make_version.py          # 更新包与版本清单生成
├── version.json             # 服务器版本清单
└── dist/                    # 打包产物
```

## 📄 许可

MIT License
