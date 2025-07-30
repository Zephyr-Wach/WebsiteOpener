# Website Opener

🌐 支持两种语言：
- [English](./README.md)
- [中文说明](./README_zh.md)

## 概述

Website Opener 是一个 Flow Launcher 插件，允许用户快速打开、管理和搜索网站。支持通过名称添加、删除和搜索网站，提供上下文菜单以复制 URL 或删除条目。提示语言可通过 `dictionary` 文件夹中的 JSON 文件动态切换（例如，中文或英文）。

## 功能
- **添加网站**：使用 `gw add <名称> <URL>` 添加网站，按回车确认。
- **删除网站**：使用 `gw remove <名称>` 删除网站，按回车确认。
- **搜索网站**：输入 `gw <关键词>` 按名称搜索网站。
- **上下文菜单**：右键点击网站结果可复制 URL 或删除网站。
- **语言切换**：使用 `gw set language <lang>`（如 `zh`、`en`）切换提示语言，保存在 `settings.json` 中。
- **Unicode 支持**：支持网站名称中的中文和其他 Unicode 字符。
- **安全性**：清理输入以防止非法字符，验证 URL 格式。

## 安装
1. **前置条件**：
   - Flow Launcher v1.20.2 或更高版本。
   - Python 3.8（例如 `D:\env\python3.8\pythonw.exe`）。
   - `requirements.txt` 中列出的依赖。
2. **安装依赖**：
   ```bash
   D:\env\python3.8\python.exe -m pip install -r requirements.txt
   ```
3. **安装插件**：
   - 将插件文件夹复制到 `C:\Users\<你的用户名>\AppData\Roaming\FlowLauncher\Plugins\goWeb`。
   - 确保包含 `plugin.json`、`main.py`、`dictionary/zh.json`、`dictionary/en.json`、`Images/app.png` 和 `requirements.txt`。
4. **验证安装**：
   - 打开 Flow Launcher（`Alt + Space`），输入 `gw`，检查插件是否加载。

## 使用方法
- **列出网站**：输入 `gw` 查看所有保存的网站，或显示列表为空的提示。
- **添加网站**：输入 `gw add grok https://grok.com`，按回车确认。
- **删除网站**：输入 `gw remove grok`，按回车确认。
- **搜索网站**：输入 `gw grok` 查找包含“grok”的网站。
- **切换语言**：输入 `gw set language en` 切换到英文提示（或 `zh` 切换到中文）。
- **上下文菜单**：右键网站结果，选择复制 URL 或删除网站。
- **示例**：
  ```bash
  gw add grok https://grok.com  # 显示“确认添加网站 grok”
  gw grok                      # 显示“打开 grok”及 URL
  gw set language en           # 切换到英文提示
  ```

## 语言支持
- **动态语言**：提示从 `dictionary/<lang>.json` 加载（如 `zh.json`、`en.json`）。
- **添加新语言**：
  1. 在 `dictionary` 文件夹创建新 JSON 文件（如 `dictionary/ja.json`），结构与 `zh.json` 一致。
  2. 示例 `ja.json`：
     ```json
     {
       "empty_list": "ウェブサイトリストが空です",
       "empty_list_sub": "'add 名前 URL' または 'remove 名前' を使用してウェブサイトを管理、または 'set language <lang>' で言語を設定",
       ...
     }
     ```
  3. 使用 `gw set language ja` 切换到新语言。
- **默认语言**：与 Flow Launcher 语言同步（`zh-CN` → `zh`, `en-US` → `en`）。

## 调试
- **日志文件**：查看 `C:\Users\<你的用户名>\AppData\Roaming\FlowLauncher\Plugins\goWeb\plugin.log` 检查错误。
- **常见问题**：
  - **语言未加载**：确保 `dictionary/<lang>.json` 存在且为有效 JSON。
  - **插件无响应**：确认 Python 3.8 和依赖（`pyflowlauncher`、`pyperclip`）。
  - **无效 URL**：URL 必须以 `http://` 或 `https://` 开头。

## 许可证
MIT 许可证。详情见 [LICENSE](LICENSE)。