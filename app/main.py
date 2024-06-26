import json
import random
import logging
from typing import List, Dict, Union
import requests
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubCrawler:
    def __init__(self, proxies: List[str]):
        self.proxies = proxies
        logger.info(f"Initialized GitHubCrawler with {len(proxies)} proxies.")

    def get_random_proxy(self) -> Dict[str, str]:
        proxy = {'http': random.choice(self.proxies)}
        logger.info(f"Using proxy: {proxy['http']}")
        return proxy

    def search_github(self, keywords: List[str], search_type: str) -> List[Dict[str, Union[str, Dict[str, str]]]]:
        base_url = "https://github.com/search"
        query = '+'.join(keywords)
        search_url = f"{base_url}?q={query}&type={search_type}"
        logger.info(f"Searching GitHub for keywords: {keywords} with type: {search_type}")
        logger.info(f"URL for search: {search_url}")

        response = self.make_request(search_url)
        if not response:
            return []

        try:
            prepared_response = json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response: {e}")
            return []

        if search_type == 'Repositories':
            return self.extract_repositories(prepared_response)
        elif search_type == 'Issues':
            return self.extract_issues(prepared_response)
        elif search_type == 'Wikis':
            return self.extract_wikis(prepared_response)

        return []

    def make_request(self, url: str) -> Union[requests.Response, None]:
        try:
            response = requests.get(url, proxies=self.get_random_proxy())
            response.raise_for_status()
            logger.info(f"Received response from URL: {url}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during request to URL {url}: {e}")
            return None

    def extract_repositories(self, data: Dict) -> List[Dict[str, Union[str, Dict[str, str]]]]:
        repositories = []
        for repository in data.get('payload', {}).get('results', []):
            repo_info = repository['repo']['repository']
            repo_url = f"https://github.com/{repo_info['owner_login']}/{repo_info['name']}"
            repositories.append({
                "url": repo_url,
                "extra": {
                    "owner": repo_info['owner_login'],
                    "language_stats": self.extract_repo_languages(repo_url)
                }
            })
        logger.info(f"Found {len(repositories)} repositories.")
        return repositories

    def extract_issues(self, data: Dict) -> List[Dict[str, str]]:
        issues = []
        for issue_block in data.get('payload', {}).get('results', []):
            repo_info = issue_block['repo']['repository']
            issues.append({
                "url": f"https://github.com/{repo_info['owner_login']}/{repo_info['name']}/issues/{issue_block['number']}"
            })
        logger.info(f"Found {len(issues)} issues.")
        return issues

    def extract_wikis(self, data: Dict) -> List[Dict[str, str]]:
        wikis = []
        for wiki_block in data.get('payload', {}).get('results', []):
            repo_info = wiki_block['repo']['repository']
            wikis.append({
                "url": f"https://github.com/{repo_info['owner_login']}/{repo_info['name']}/wiki/{wiki_block['path'][:-3]}"
            })
        logger.info(f"Found {len(wikis)} wikis.")
        return wikis

    def extract_repo_languages(self, repo_url: str) -> Dict[str, str]:
        response = self.make_request(repo_url)
        if not response:
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        language_stats = {}

        progress_items = soup.find_all('span', class_='Progress-item')
        for item in progress_items:
            language = item.get('aria-label', '').rsplit(' ', 1)
            if len(language) == 2:
                language_stats[language[0]] = language[1]

        return language_stats


def main():
    with open('input-example.json', 'r') as file:
        input_data = json.load(file)

    keywords = input_data["keywords"]
    search_type = input_data["type"]
    proxies = input_data["proxies"]

    crawler = GitHubCrawler(proxies)
    results = crawler.search_github(keywords, search_type)

    output = [{"url": result["url"]} for result in results]

    with open('output.json', 'w') as file:
        json.dump(output, file, indent=2)

    print("Results written to output.json")


if __name__ == "__main__":
    main()
