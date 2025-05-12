# JournalFetcher 📚

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini API](https://img.shields.io/badge/Gemini-API-orange)](https://ai.google.dev/)

基于 Google Gemini 的智能学术论文抓取工具，可以自动检索和下载指定期刊的文章。

[English](README_EN.md) | [中文](README.md)

## ✨ 功能特点

- 🔍 支持指定期刊名称和期数进行文章检索
- 🔗 自动搜索文章的工作论文或预印本链接
- 📥 智能下载 PDF 或其他格式的论文文件
- 📁 自动创建分类目录结构
- 📊 显示下载进度条
- 📦 支持批量下载多篇文章

## 🚀 快速开始

### 安装要求

```bash
pip install google-genai requests beautifulsoup4 tqdm
```

### 使用方法

1. 运行程序：
```bash
python src/main.py
```

2. 按提示输入：
   - 期刊名称（默认为：Journal of Political Economy）
   - 期刊年份和期数（默认为：2025年第四期）
   - Gemini Api 密钥（如未设置为环境变量）

3. 程序会自动：
   - 检索指定期刊的文章列表
   - 搜索每篇文章的可下载链接
   - 下载文章到本地目录

## 📂 文件存储结构

下载的文件将保存在 `downloads` 目录下，按照以下结构组织：

```
downloads/
  └── [期刊名称]/
      └── [期刊期数]/
          ├── [文件目录.md]
          └── [文章标题] - [作者] - [期刊信息].[文件格式]
```

## ⚠️ 注意事项

- 需要有效的 Google Gemini API 密钥
- 下载的文件名会自动清理不合法字符
- 如果找不到文章链接，会显示"Not found"
- 支持下载 PDF、DOC、DOCX 等格式的文件

## 📋 项目结构

```
.
├── src/                    # 源代码目录
├── .env.example           # 环境变量模板
├── requirements.txt       # 项目依赖
└── README.md             # 项目文档
```

## 🔧 环境设置

1. 克隆项目：
```bash
git clone https://github.com/yourusername/ai-grasp-articles.git
cd ai-grasp-articles
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
```
然后编辑 `.env` 文件，填入您的 API keys。

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---
⭐ 如果这个项目对您有帮助，请给我们一个 star！
