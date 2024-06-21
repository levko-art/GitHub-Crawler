# GitHub-Crawler
## Overview
GitHub Crawler is a Python-based tool that allows users to search for repositories, issues, and wikis on GitHub using a list of proxies. It handles the search process, makes requests through random proxies, and extracts relevant information from the search results.

## Features
Search GitHub Repositories, Issues, and Wikis: Search for specific keywords in GitHub repositories, issues, or wikis.
Proxy Support: Rotate between multiple proxies to avoid rate limits and IP bans.
Language Statistics Extraction: Retrieve language statistics for repositories.

## Requirements
Python 3.x
requests
beautifulsoup4
pyyaml

## Installation
1. Clone the repository:
```
git clone https://github.com/levko-art/GitHub-Crawler.git
cd github-crawler
```

2. Install the required dependencies:
```
pip install requests beautifulsoup4 pyyaml
```

3. Prepare the proxies.yaml file with your proxy list

4. Run Python script
```
python github_crawler.py
```
And follow instructions

