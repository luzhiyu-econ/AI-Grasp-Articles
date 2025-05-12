import base64
import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
from google import genai
from google.genai import types
from urllib.parse import urlparse, unquote

def get_api_key():
    """获取API密钥，优先从环境变量获取，如果没有则要求用户输入"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n未找到环境变量 GEMINI_API_KEY")
        print("请从 https://makersuite.google.com/app/apikey 获取API密钥")
        api_key = input("请输入您的Google Gemini API密钥: ").strip()
        if not api_key:
            raise ValueError("API密钥不能为空")
    return api_key

def generate_journal_articles():
    # 获取用户输入
    journal_name = input("请输入期刊名称 (默认: Journal of Political Economy): ") or "Journal of Political Economy"
    journal_issue = input("请输入期刊年份和期数 (默认: 2025年第四期): ") or "2025年第四期"
    
    # 构建查询文本
    query_text = f"为我检索{journal_name} {journal_issue}包含哪些文章，并以json格式返回，包含 article_title 和 author 两项。"
    
    # 获取API密钥
    api_key = get_api_key()
    
    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.5-flash-preview-04-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""请按照以下要求检索文章信息：
{query_text}

请确保 article_title 是文章的完整标题。
请确保 author 是文章的主要作者或所有作者列表（如果可以获取）。
JSON 格式应该如下：
{{
  \"articles\": [
    {{
      \"article_title\": \"文章标题示例1\",
      \"author\": \"作者A\"
    }},
    {{
      \"article_title\": \"文章标题示例2\",
      \"author\": \"作者B, 作者C\"
    }}
  ]
}}
请严格按照此JSON结构返回，不要添加任何额外的解释性文字在JSON本身之外。直接开始JSON输出。"""),
            ],
        ),
    ]
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        tools=tools,
        response_mime_type="text/plain",
    )

    # 用于存储完整响应内容
    full_response = ""
    
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
        full_response += chunk.text
    
    # 将结果保存为JSON变量
    try:
        # 移除可能的前缀和后缀内容，尝试提取JSON部分
        json_str = full_response.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        result_json = json.loads(json_str)
        print("\n\n结果已保存到变量 result_json")
        return result_json, json_str, journal_name, journal_issue
    except json.JSONDecodeError as e:
        print(f"\n\n无法将响应解析为有效的JSON格式: {e}")
        return {"error": "Invalid JSON response", "raw_response": full_response}, full_response, journal_name, journal_issue

def find_article_links(journal_data_str):
    # 获取API密钥
    api_key = get_api_key()
    
    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.5-flash-preview-04-17"
    
    prompt_text = """need you to find accessible, free, working paper or pre-print links for the following list of academic articles. Please structure your response in JSON format. The main JSON object should contain a key called \"article_links\", which is an array of objects. Each object in this array should represent an article and have two keys: \"article_name\" (the title of the article I provide) and \"working_paper_link\" (the URL to the accessible paper you find). If you cannot find an accessible link for a particular article, please use the string \"Not found\" for its \"working_paper_link\".Here is the list of articles:

""" + journal_data_str + """

Please begin your JSON output now."""
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        tools=tools,
        response_mime_type="text/plain",
    )

    # 收集完整响应
    full_response = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
        full_response += chunk.text
    
    # 将结果保存为JSON变量
    try:
        # 移除可能的前缀和后缀内容，尝试提取JSON部分
        json_str = full_response.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        links_json = json.loads(json_str)
        print("\n\n论文链接已保存到变量 links_json")
        return links_json
    except json.JSONDecodeError as e:
        print(f"\n\n无法将响应解析为有效的JSON格式: {e}")

def sanitize_filename(name):
    """清理文件名，移除不允许的字符"""
    # 替换不允许在文件名中使用的字符（Windows、Linux、macOS 通用）
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # 去除开头和结尾的点号（Windows 不允许）
    name = name.strip('.')
    # 去除多余的空格
    name = re.sub(r'\s+', " ", name).strip()
    # 限制长度（考虑不同操作系统的限制）
    # Windows 路径最大长度为 260 字符，macOS 和 Linux 为 255 字符
    if len(name) > 150:  # 留出足够空间给路径前缀
        name = name[:147] + "..."
    return name

def download_paper(url, title, author, journal_name, journal_issue, directory):
    """下载论文并保存到指定目录"""
    if url == "Not found":
        print(f"未找到《{title}》的下载链接")
        return False
    
    try:
        # 创建目录结构
        journal_folder = sanitize_filename(journal_name)
        issue_folder = sanitize_filename(journal_issue)
        save_dir = Path(directory) / journal_folder / issue_folder
        
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"错误：没有权限创建目录 {save_dir}")
            return False
        except OSError as e:
            print(f"创建目录时出错：{e}")
            return False
        
        # 构建文件名
        filename = sanitize_filename(f"{title} - {author} - {journal_name} {journal_issue}")
        
        # 首先发送请求获取重定向的实际URL
        session = requests.Session()
        response = session.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()
        final_url = response.url
        
        # 尝试从URL或内容类型确定文件扩展名
        content_type = response.headers.get('Content-Type', '')
        
        if 'pdf' in content_type.lower():
            ext = '.pdf'
        elif 'application/msword' in content_type.lower():
            ext = '.doc'
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type.lower():
            ext = '.docx'
        else:
            # 尝试从URL中获取扩展名
            parsed_url = urlparse(final_url)
            path = unquote(parsed_url.path)
            ext = Path(path).suffix
            if not ext or len(ext) > 5:
                # 默认为PDF，如果无法确定
                ext = '.pdf'
        
        filepath = save_dir / f"{filename}{ext}"
        
        # 获取文件大小用于进度显示
        file_size = int(response.headers.get('Content-Length', 0))
        
        # 下载文件并显示进度条
        print(f"下载: {title}{ext}")
        with open(filepath, 'wb') as f, tqdm(
            desc=f"下载 {title}",
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        
        print(f"已保存: {filepath}")
        return True
    except Exception as e:
        print(f"下载 '{title}' 时出错: {e}")
        return False

def process_and_download_papers(articles_json, links_json, journal_name, journal_issue, download_dir="downloads"):
    """处理文章列表和下载相应的论文"""
    print("\n\n=== 文章列表及论文链接 ===\n")
    
    # 确保下载目录使用绝对路径
    download_dir = Path(download_dir).resolve()
    print(f"下载目录: {download_dir}")
    
    articles = articles_json.get("articles", [])
    article_links = links_json.get("article_links", [])
    
    # 创建文章标题到链接的映射表
    links_map = {item["article_name"]: item["working_paper_link"] for item in article_links}
    
    success_count = 0
    for article in articles:
        title = article.get("article_title", "Unknown title")
        author = article.get("author", "Unknown author")
        
        # 查找最匹配的链接（可能标题不完全一致）
        link = None
        for link_title, link_url in links_map.items():
            if title == link_title:
                link = link_url
                break
        
        if not link:
            # 如果没找到精确匹配，尝试部分匹配
            best_match = None
            for link_title, link_url in links_map.items():
                if title in link_title or link_title in title:
                    best_match = link_url
                    break
            link = best_match or "Not found"
        
        print(f"标题: {title}")
        print(f"作者: {author}")
        print(f"论文链接: {link}")
        
        # 下载论文
        if download_paper(link, title, author, journal_name, journal_issue, download_dir):
            success_count += 1
        
        print("-" * 80)
    
    # 统计可用链接和下载数量
    available_links = sum(1 for link in links_map.values() if link != "Not found")
    print(f"\n总结: 共有{len(articles)}篇文章，找到了{available_links}篇的工作论文链接，成功下载了{success_count}篇")

def generate_markdown_table(articles_json, links_json, journal_name, journal_issue):
    """生成包含文章信息的Markdown表格"""
    articles = articles_json.get("articles", [])
    article_links = links_json.get("article_links", [])
    
    # 创建文章标题到链接的映射表
    links_map = {item["article_name"]: item["working_paper_link"] for item in article_links}
    
    # 构建Markdown表格
    markdown_content = f"# {journal_name} {journal_issue} 文章列表\n\n"
    markdown_content += "| 标题 | 作者 | 论文链接 |\n"
    markdown_content += "|------|------|----------|\n"
    
    for article in articles:
        title = article.get("article_title", "Unknown title")
        author = article.get("author", "Unknown author")
        
        # 查找最匹配的链接
        link = None
        for link_title, link_url in links_map.items():
            if title == link_title:
                link = link_url
                break
        
        if not link:
            # 如果没找到精确匹配，尝试部分匹配
            for link_title, link_url in links_map.items():
                if title in link_title or link_title in title:
                    link = link_url
                    break
        
        if not link:
            link = "Not found"
            
        # 转义Markdown特殊字符
        title = title.replace("|", "\\|")
        author = author.replace("|", "\\|")
        
        # 添加表格行
        markdown_content += f"| {title} | {author} | {link} |\n"
    
    # 保存到文件
    journal_folder = sanitize_filename(journal_name)
    issue_folder = sanitize_filename(journal_issue)
    save_dir = Path("downloads") / journal_folder / issue_folder
    save_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = save_dir / "articles_table.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"\n文章信息表格已保存到: {filepath}")
    return filepath

if __name__ == "__main__":
    # 获取期刊文章列表
    result_json, json_str, journal_name, journal_issue = generate_journal_articles()
    print("\n\n正在搜索文章的工作论文链接...\n")
    
    # 将获取的JSON结果传入第二个函数
    links_json = find_article_links(json_str)
    
    # 处理结果并下载论文
    process_and_download_papers(result_json, links_json, journal_name, journal_issue)
    
    # 生成并保存Markdown表格
    generate_markdown_table(result_json, links_json, journal_name, journal_issue)
