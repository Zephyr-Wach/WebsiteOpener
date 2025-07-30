# Website Opener

🌐 Supporting multiple languages:
- [English](./README.md)
- [中文说明](./README_zh.md)

## Overview

Website Opener is a Flow Launcher plugin that enables users to quickly open, manage, and search websites. It supports adding, removing, and searching websites by name, with a context menu for copying URLs or deleting entries. Language prompts can be switched dynamically (e.g., English or Chinese) using JSON files in the `dictionary` folder.

## Features
- **Add Websites**: Use `gw add <name> <url>` to add a website, confirmed by pressing Enter.
- **Remove Websites**: Use `gw remove <name>` to delete a website, confirmed by pressing Enter.
- **Search Websites**: Enter `gw <keyword>` to search websites by name.
- **Context Menu**: Right-click a website to copy its URL or delete it.
- **Language Switching**: Use `gw set language <lang>` (e.g., `zh`, `en`) to switch prompt languages, stored in `settings.json`.
- **Unicode Support**: Supports Chinese and other Unicode characters in website names.
- **Security**: Sanitizes inputs to prevent invalid characters and validates URLs.

## Installation
1. **Prerequisites**:
   - Flow Launcher v1.20.2 or later.
   - Python 3.8 (e.g., `D:\env\python3.8\pythonw.exe`).
   - Dependencies listed in `requirements.txt`.
2. **Install Dependencies**:
   ```bash
   D:\env\python3.8\python.exe -m pip install -r requirements.txt
   ```
3. **Install Plugin**:
   - Copy the plugin folder to `C:\Users\<YourUsername>\AppData\Roaming\FlowLauncher\Plugins\goWeb`.
   - Ensure `plugin.json`, `main.py`, `dictionary/zh.json`, `dictionary/en.json`, `Images/app.png`, and `requirements.txt` are included.
4. **Verify Setup**:
   - Open Flow Launcher (`Alt + Space`), type `gw`, and check if the plugin loads.

## Usage
- **List Websites**: Type `gw` to view all saved websites or a message if the list is empty.
- **Add Website**: Type `gw add grok https://grok.com`, then press Enter to confirm.
- **Remove Website**: Type `gw remove grok`, then press Enter to confirm.
- **Search Website**: Type `gw grok` to find websites containing "grok".
- **Switch Language**: Type `gw set language en` to switch to English prompts (or `zh` for Chinese).
- **Context Menu**: Right-click a website result to copy its URL or delete it.
- **Example**:
  ```bash
  gw add grok https://grok.com  # Shows "Confirm adding website grok"
  gw grok                      # Shows "Open grok" with URL
  gw set language zh           # Switches to Chinese prompts
  ```

## Language Support
- **Dynamic Languages**: Prompts are loaded from `dictionary/<lang>.json` (e.g., `zh.json`, `en.json`).
- **Add New Language**:
  1. Create a new JSON file (e.g., `dictionary/ja.json`) with the same structure as `zh.json`.
  2. Example `ja.json`:
     ```json
     {
       "empty_list": "ウェブサイトリストが空です",
       "empty_list_sub": "'add 名前 URL' または 'remove 名前' を使用してウェブサイトを管理、または 'set language <lang>' で言語を設定",
       ...
     }
     ```
  3. Use `gw set language ja` to switch to the new language.
- **Default Language**: Syncs with Flow Launcher’s language (`zh-CN` → `zh`, `en-US` → `en`).

## Debugging
- **Log File**: Check `C:\Users\<YourUsername>\AppData\Roaming\FlowLauncher\Plugins\goWeb\plugin.log` for errors.
- **Common Issues**:
  - **Language not loading**: Ensure `dictionary/<lang>.json` exists and is valid JSON.
  - **Plugin not responding**: Verify Python 3.8 and dependencies (`pyflowlauncher`, `pyperclip`).
  - **Invalid URL**: URLs must start with `http://` or `https://`.

## License
MIT License. See [LICENSE](LICENSE) for details.