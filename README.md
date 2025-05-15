# JournalFetcher 📚

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini API](https://img.shields.io/badge/Gemini-API-orange)](https://ai.google.dev/)

An intelligent academic paper fetching tool based on Google Gemini, capable of automatically retrieving and downloading articles from specified journals.

[English](README.md) | [中文](README_zh.md)

## ✨ Features

- 🔍 Support for journal name and issue number specification
- 🔗 Automatic search for working paper or preprint links
- 📥 Smart download of PDF or other format files
- 📁 Automatic creation of categorized directory structure
- 📊 Download progress bar display
- 📦 Support for batch downloading multiple articles

## 🚀 Quick Start

### Requirements

```bash
pip install google-genai requests beautifulsoup4 tqdm
```

### Usage

1. Run the program:
```bash
python src/main.py
```

2. Follow the prompts to enter:
   - Journal name (default: Journal of Political Economy)
   - Journal year and issue number (default: 2025 Issue 4)
   - Gemini API key (if not set as environment variable)

3. The program will automatically:
   - Retrieve the article list for the specified journal
   - Search for downloadable links for each article
   - Download articles to local directory

## 📂 File Storage Structure

Downloaded files will be saved in the `downloads` directory with the following structure:

```
downloads/
  └── [Journal Name]/
      └── [Issue Number]/
          ├── [File Directory.md]
          └── [Article Title] - [Author] - [Journal Info].[File Format]
```

## ⚠️ Notes

- Valid Google Gemini API key required
- Downloaded filenames are automatically sanitized
- "Not found" will be displayed if article link is not found
- Supports downloading PDF, DOC, DOCX and other file formats

## 📋 Project Structure

```
.
├── src/                    # Source code directory
├── .env.example           # Environment variables template
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## 🔧 Environment Setup

1. Clone the project:
```bash
git clone https://github.com/yourusername/ai-grasp-articles.git
cd ai-grasp-articles
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```
Then edit the `.env` file and add your API keys.

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---
⭐ If you find this project helpful, please give us a star! 
