from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pathlib import Path
import json
import subprocess
import webbrowser
import unicodedata
import re
import logging
import pyperclip
from typing import List, Dict, Optional

# 设置日志
logging.basicConfig(
    filename=Path(__file__).parent / "plugin.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 插件目录绝对路径
plugindir = Path(__file__).parent.absolute()
SITE_FILE = plugindir / "sites.json"
SETTINGS_FILE = plugindir / "settings.json"
DICTIONARY_DIR = plugindir / "dictionary"

def sanitize_string(s: str) -> str:
    """清理字符串，确保只包含有效的 UTF-8 字符，保留中文和常见字符"""
    if not s:
        logging.warning("sanitize_string received empty or None string")
        return ""
    try:
        logging.debug(f"Original string: {repr(s)} (hex: {s.encode('utf-8', errors='replace').hex()})")
        s = unicodedata.normalize("NFKC", s)
        s = re.sub(r'[^\x20-\x7E\u4E00-\u9FFF\u00A0-\uD7FF\uE000-\uFFFF]', '', s)
        s = re.sub(r'[\x00-\x1F\x7F]', '', s)
        cleaned = s.strip()
        logging.debug(f"Sanitized string: {repr(cleaned)} (hex: {cleaned.encode('utf-8', errors='replace').hex()})")
        return cleaned
    except Exception as e:
        logging.error(f"Error sanitizing string {repr(s)}: {str(e)}")
        return ""

def is_valid_url(url: str) -> bool:
    """验证 URL 是否合法"""
    url_pattern = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # 可选端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

def load_sites() -> Dict[str, str]:
    """加载 sites.json"""
    if not SITE_FILE.exists():
        logging.info("sites.json does not exist, returning empty dict")
        return {}
    try:
        with open(SITE_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            logging.debug(f"Loaded sites.json: {data}")
            cleaned_data = {}
            for k, v in data.items():
                cleaned_key = sanitize_string(k) if k else ""
                cleaned_value = sanitize_string(v) if v else ""
                if cleaned_key and cleaned_value and is_valid_url(cleaned_value):
                    cleaned_data[cleaned_key] = cleaned_value
                else:
                    logging.warning(f"Skipping invalid site entry: key={k}, value={v}")
            return cleaned_data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f"Error loading sites.json: {str(e)}")
        return {}

def save_sites(data: Dict[str, str]):
    """保存 sites.json"""
    try:
        cleaned_data = {}
        for k, v in data.items():
            cleaned_key = sanitize_string(k) if k else ""
            cleaned_value = sanitize_string(v) if v else ""
            if cleaned_key and cleaned_value and is_valid_url(cleaned_value):
                cleaned_data[cleaned_key] = cleaned_value
            else:
                logging.warning(f"Skipping invalid site entry during save: key={k}, value={v}")
        with open(SITE_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved sites.json: {cleaned_data}")
    except Exception as e:
        logging.error(f"Error saving sites.json: {str(e)}")

def get_flow_language() -> str:
    """获取 Flow Launcher 的语言设置，映射到 zh 或 en"""
    flow_settings = Path.home() / "AppData/Roaming/FlowLauncher/UserData/Settings/Settings.json"
    try:
        if flow_settings.exists():
            with open(flow_settings, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang = data.get("Language", "en-US")
                logging.debug(f"Flow Launcher language: {lang}")
                return "zh" if lang.startswith("zh") else "en"
        logging.warning("Flow Launcher settings file not found, defaulting to en")
        return "en"
    except Exception as e:
        logging.error(f"Error reading Flow Launcher settings: {str(e)}")
        return "en"

def load_settings() -> Dict[str, str]:
    """加载 settings.json"""
    if not SETTINGS_FILE.exists():
        settings = {"language": get_flow_language()}
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            logging.info(f"Created settings.json with default language: {settings['language']}")
        except Exception as e:
            logging.error(f"Error creating settings.json: {str(e)}")
        return settings
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            logging.debug(f"Loaded settings.json: {settings}")
            # 确保语言设置存在
            if "language" not in settings:
                settings["language"] = get_flow_language()
                save_settings(settings)
            return settings
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f"Error loading settings.json: {str(e)}")
        return {"language": get_flow_language()}

def save_settings(settings: Dict[str, str]):
    """保存 settings.json"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved settings.json: {settings}")
    except Exception as e:
        logging.error(f"Error saving settings.json: {str(e)}")

def load_language_messages(language: str) -> Dict[str, str]:
    """加载指定语言的提示消息"""
    language_file = DICTIONARY_DIR / f"{language}.json"
    default_language = "zh"
    try:
        if not language_file.exists():
            logging.warning(f"Language file {language_file} not found, falling back to {default_language}")
            language_file = DICTIONARY_DIR / f"{default_language}.json"
            if not language_file.exists():
                logging.error(f"Default language file {language_file} not found, returning empty dict")
                return {}
        with open(language_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
            logging.debug(f"Loaded language messages for {language}: {messages}")
            return messages
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f"Error loading language file {language_file}: {str(e)}")
        return load_language_messages(default_language)

def get_available_languages() -> List[str]:
    """获取 dictionary 文件夹中可用的语言列表"""
    if not DICTIONARY_DIR.exists():
        logging.error("Dictionary directory does not exist")
        return ["zh", "en"]
    languages = [f.stem for f in DICTIONARY_DIR.glob("*.json")]
    logging.debug(f"Available languages: {languages}")
    return languages

def create_result(title: str, subtitle: str, action: Optional[Dict] = None, score: int = 100, language: str = "zh", context_data: Optional[Dict] = None) -> Result:
    """生成统一格式的 Result 对象，基于语言选择提示"""
    messages = load_language_messages(language)
    try:
        title = title.format(**messages)
        subtitle = subtitle.format(**messages)
    except KeyError as e:
        logging.warning(f"Missing message key {e} for language {language}, using raw string")
    result = Result(
        Title=title,
        SubTitle=subtitle,
        IcoPath="Images/app.png",
        JsonRPCAction=action,
        Score=score
    )
    if context_data:
        result.ContextData = context_data
    return result

def handle_add_query(input_str: str, sites: Dict[str, str], language: str) -> List[Result]:
    """处理 add 命令"""
    results = []
    parts = input_str.split(" ", 1)
    messages = load_language_messages(language)
    
    if len(parts) < 2 or not parts[1].strip():
        return [create_result(
            messages.get("invalid_add_format", "请输入完整的网站名称和 URL"),
            messages.get("invalid_add_format_sub", "当前输入：{input}，格式应为：add 名称 URL").format(input=input_str),
            language=language
        )]
    
    name, url = parts
    name = sanitize_string(name)
    url = sanitize_string(url)
    
    # 验证规则
    validations = [
        (not name, messages.get("invalid_name", "请输入有效的网站名称"), 
         messages.get("invalid_name_sub", "当前输入：{input}，名称不能为空").format(input=input_str)),
        (not url, messages.get("invalid_url", "请输入有效的 URL"), 
         messages.get("invalid_url_sub", "当前输入：{input}，URL 不能为空").format(input=input_str)),
        (not url.startswith(('http://', 'https://')), messages.get("invalid_url_format", "URL 格式错误"), 
         messages.get("invalid_url_format_sub", "当前输入：{input}，URL 必须以 http:// 或 https:// 开头").format(input=input_str)),
        (not is_valid_url(url), messages.get("invalid_url_valid", "URL 格式无效"), 
         messages.get("invalid_url_valid_sub", "当前输入：{input}，请输入有效的 URL").format(input=input_str)),
        (name in sites, messages.get("name_exists", "网站名称 {name} 已存在").format(name=name), 
         messages.get("name_exists_sub", "当前输入：{input}，请使用其他名称").format(input=input_str))
    ]
    
    for condition, title, subtitle in validations:
        if condition:
            return [create_result(title, subtitle, language=language)]
    
    # 提供确认选项
    return [create_result(
        messages.get("confirm_add", "确认添加网站 {name}").format(name=name),
        messages.get("confirm_add_sub", "URL: {url}，按回车确认保存").format(url=url),
        {"method": "add_site", "parameters": [name, url]},
        language=language
    )]

def handle_remove_query(input_str: str, sites: Dict[str, str], language: str) -> List[Result]:
    """处理 remove 命令"""
    messages = load_language_messages(language)
    name = sanitize_string(input_str)
    
    if not name:
        return [create_result(
            messages.get("invalid_remove_format", "请输入要删除的网站名称"),
            messages.get("invalid_remove_format_sub", "当前输入：{input}，格式应为：remove 名称").format(input=input_str),
            language=language
        )]
    
    if name not in sites:
        return [create_result(
            messages.get("name_not_exists", "网站 {name} 不存在").format(name=name),
            messages.get("name_not_exists_sub", "当前输入：{input}，请输入存在的网站名称").format(input=input_str),
            language=language
        )]
    
    return [create_result(
        messages.get("confirm_remove", "确认删除网站 {name}").format(name=name),
        messages.get("confirm_remove_sub", "URL: {url}，按回车确认删除").format(url=sites[name]),
        {"method": "remove_site", "parameters": [name]},
        language=language
    )]

def handle_search_query(keyword: str, sites: Dict[str, str], language: str) -> List[Result]:
    """处理搜索命令"""
    results = []
    messages = load_language_messages(language)
    keyword = sanitize_string(keyword).lower()
    
    for name, url in sites.items():
        if keyword in sanitize_string(name).lower():
            results.append(create_result(
                messages.get("open_site", "打开 {name}").format(name=sanitize_string(name)),
                sanitize_string(url),
                {"method": "open_url", "parameters": [url]},
                score=90,
                language=language,
                context_data={"name": name, "url": url}
            ))
    
    if not results:
        results.append(create_result(
            messages.get("no_match", "未找到匹配的网站"),
            messages.get("no_match_sub", "关键词：{keyword}，请尝试其他关键词或添加网站").format(keyword=keyword),
            language=language
        ))
    return results

def handle_settings_query(input_str: str, settings: Dict[str, str], language: str) -> List[Result]:
    """处理 set 命令"""
    results = []
    messages = load_language_messages(language)
    available_languages = get_available_languages()
    
    parts = input_str.strip().split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        return [create_result(
            messages.get("invalid_set_format", "请输入有效的设置命令"),
            messages.get("invalid_set_format_sub", "当前输入：{input}，格式应为：set language <lang>").format(input=input_str),
            language=language
        )]
    
    command, value = parts
    if command != "language":
        return [create_result(
            messages.get("invalid_set_format", "请输入有效的设置命令"),
            messages.get("invalid_set_format_sub", "当前输入：{input}，格式应为：set language <lang>").format(input=input_str),
            language=language
        )]
    
    if value not in available_languages:
        return [create_result(
            messages.get("invalid_language", "无效的语言选项"),
            messages.get("invalid_language_sub", "当前输入：{input}，支持的语言：{languages}").format(input=input_str, languages=", ".join(available_languages)),
            language=language
        )]
    
    return [create_result(
        messages.get("set_language_success", "语言已设置为 {lang}").format(lang=value),
        messages.get("set_language_success_sub", "设置已保存"),
        {"method": "set_language", "parameters": [value]},
        language=language
    )]

plugin = Plugin()

@plugin.on_method
def query(query: str) -> ResultResponse:
    """处理查询"""
    q = sanitize_string(query).strip() if query else ""
    logging.debug(f"Raw query: {repr(query)} (hex: {query.encode('utf-8', errors='replace').hex()})")
    logging.debug(f"Sanitized query: {repr(q)} (hex: {q.encode('utf-8', errors='replace').hex()})")
    sites = load_sites()
    settings = load_settings()
    language = settings.get("language", "zh")
    results = []

    if q == "":
        if not sites:
            results = [create_result(
                MESSAGES.get("empty_list", "网站列表为空"),
                MESSAGES.get("empty_list_sub", "请用 'add 名称 URL' 或 'remove 名称' 管理网站，或用 'set language <lang>' 设置语言"),
                language=language
            )]
        else:
            results = [
                create_result(
                    sanitize_string(name),
                    sanitize_string(url),
                    {"method": "open_url", "parameters": [url]},
                    score=90,
                    language=language,
                    context_data={"name": name, "url": url}
                )
                for name, url in sites.items()
            ]
    elif q.startswith("add "):
        results = handle_add_query(q[4:].strip(), sites, language)
    elif q.startswith("remove "):
        results = handle_remove_query(q[7:].strip(), sites, language)
    elif q.startswith("set "):
        results = handle_settings_query(q[4:].strip(), settings, language)
    else:
        results = handle_search_query(q, sites, language)

    logging.debug(f"Query results: {results}")
    return send_results(results)

@plugin.on_method
def add_site(name: str, url: str) -> ResultResponse:
    """执行添加网站操作"""
    settings = load_settings()
    language = settings.get("language", "zh")
    messages = load_language_messages(language)
    try:
        sites = load_sites()
        name = sanitize_string(name)
        url = sanitize_string(url)
        if not name:
            raise ValueError(messages.get("invalid_name", "请输入有效的网站名称"))
        if name in sites:
            raise ValueError(messages.get("name_exists", "网站名称 {name} 已存在").format(name=name))
        if not url:
            raise ValueError(messages.get("invalid_url", "请输入有效的 URL"))
        if not url.startswith(('http://', 'https://')):
            raise ValueError(messages.get("invalid_url_format", "URL 格式错误"))
        if not is_valid_url(url):
            raise ValueError(messages.get("invalid_url_valid", "URL 格式无效"))
        sites[name] = url
        save_sites(sites)
        logging.info(f"Added site: {name} -> {url}")
        return send_results([create_result(
            messages.get("add_success", "已添加网站 {name}").format(name=name),
            messages.get("add_success_sub", "{url}").format(url=url),
            language=language
        )])
    except Exception as e:
        logging.error(f"Error adding site {name}: {str(e)}")
        return send_results([create_result(
            messages.get("add_failed", "添加失败"),
            messages.get("add_failed_sub", "错误：{error}").format(error=str(e)),
            language=language
        )])

@plugin.on_method
def set_language(lang: str) -> ResultResponse:
    """设置语言"""
    settings = load_settings()
    language = settings.get("language", "zh")
    messages = load_language_messages(language)
    available_languages = get_available_languages()
    try:
        if lang not in available_languages:
            raise ValueError(messages.get("invalid_language", "无效的语言选项"))
        settings["language"] = lang
        save_settings(settings)
        logging.info(f"Language set to: {lang}")
        return send_results([create_result(
            messages.get("set_language_success", "语言已设置为 {lang}").format(lang=lang),
            messages.get("set_language_success_sub", "设置已保存"),
            language=language
        )])
    except Exception as e:
        logging.error(f"Error setting language {lang}: {str(e)}")
        return send_results([create_result(
            messages.get("add_failed", "添加失败"),
            messages.get("add_failed_sub", "错误：{error}").format(error=str(e)),
            language=language
        )])

@plugin.on_method
def open_url(url: str) -> ResultResponse:
    """打开 URL"""
    settings = load_settings()
    language = settings.get("language", "zh")
    messages = load_language_messages(language)
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError(messages.get("invalid_url_format", "URL 格式错误"))
        subprocess.run(['start', '', url], shell=True, check=True)
        logging.info(f"Opened URL: {url} with default browser (subprocess)")
        return send_results([])
    except Exception as e:
        logging.warning(f"subprocess.run failed for URL {url}: {str(e)}, falling back to webbrowser")
        try:
            webbrowser.open(url)
            logging.info(f"Opened URL: {url} with default browser (webbrowser)")
            return send_results([])
        except Exception as e2:
            logging.error(f"Error opening URL {url}: subprocess error: {str(e)}, webbrowser error: {str(e2)}")
            return send_results([create_result(
                messages.get("open_url_failed", "打开 URL 失败"),
                messages.get("open_url_failed_sub", "错误：{error}").format(error=str(e2)),
                language=language
            )])

@plugin.on_method
def copy_to_clipboard(text: str) -> ResultResponse:
    """复制到剪贴板"""
    settings = load_settings()
    language = settings.get("language", "zh")
    messages = load_language_messages(language)
    try:
        pyperclip.copy(text)
        logging.info(f"Copied to clipboard: {text}")
        return send_results([create_result(
            messages.get("copy_success", "已复制到剪贴板"),
            messages.get("copy_success_sub", "{text}").format(text=text[:100] + "..." if len(text) > 100 else text),
            language=language
        )])
    except Exception as e:
        logging.error(f"Error copying to clipboard: {str(e)}")
        return send_results([create_result(
            messages.get("copy_failed", "复制失败"),
            messages.get("copy_failed_sub", "错误：{error}").format(error=str(e)),
            language=language
        )])

@plugin.on_method
def context_menu(data: dict) -> ResultResponse:
    """为网站结果提供上下文菜单，支持复制 URL 和删除网站"""
    settings = load_settings()
    language = settings.get("language", "zh")
    messages = load_language_messages(language)
    name = data.get("name", "")
    url = data.get("url", "")
    results = [
        create_result(
            messages.get("copy_url", "复制 {name} 的 URL").format(name=name),
            url,
            {"method": "copy_to_clipboard", "parameters": [url]},
            language=language
        ),
        create_result(
            messages.get("delete_site", "删除网站 {name}").format(name=name),
            messages.get("delete_site_sub", "从列表中移除 {name}").format(name=name),
            {"method": "remove_site", "parameters": [name]},
            language=language
        )
    ]
    logging.debug(f"Context menu for {name}: {results}")
    return send_results(results)

@plugin.on_method
def remove_site(name: str) -> ResultResponse:
    """执行删除网站操作"""
    settings = load_settings()
    language = settings.get("language", "zh")
    messages = load_language_messages(language)
    try:
        sites = load_sites()
        name = sanitize_string(name)
        if name not in sites:
            raise ValueError(messages.get("name_not_exists", "网站 {name} 不存在").format(name=name))
        del sites[name]
        save_sites(sites)
        logging.info(f"Removed site: {name}")
        return send_results([create_result(
            messages.get("remove_success", "已删除网站 {name}").format(name=name),
            messages.get("remove_success_sub", "网站已从列表中移除"),
            language=language
        )])
    except Exception as e:
        logging.error(f"Error removing site {name}: {str(e)}")
        return send_results([create_result(
            messages.get("remove_failed", "删除失败"),
            messages.get("remove_failed_sub", "错误：{error}").format(error=str(e)),
            language=language
        )])

if __name__ == "__main__":
    # 确保 dictionary 文件夹存在
    DICTIONARY_DIR.mkdir(exist_ok=True)
    plugin.run()