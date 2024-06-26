import json
import unittest
from unittest.mock import patch, MagicMock
import requests
from app.main import GitHubCrawler


class TestGitHubCrawler(unittest.TestCase):

    def setUp(self):
        self.proxies = ['http://proxy1', 'http://proxy2']
        self.crawler = GitHubCrawler(self.proxies)

    @patch('app.main.requests.get')
    def test_make_request_success(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = 'https://github.com/search?q=test&type=Repositories'
        response = self.crawler.make_request(url)

        mock_get.assert_called_once()
        self.assertEqual(response, mock_response)

    @patch('app.main.requests.get')
    def test_make_request_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        url = 'https://github.com/search?q=test&type=Repositories'
        response = self.crawler.make_request(url)

        mock_get.assert_called_once()
        self.assertIsNone(response)

    @patch('app.main.GitHubCrawler.make_request')
    def test_search_github_repositories(self, mock_make_request):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "payload": {
                "results": [
                    {
                        "repo": {
                            "repository": {
                                "owner_login": "test_owner",
                                "name": "test_repo"
                            }
                        }
                    }
                ]
            }
        })
        mock_make_request.return_value = mock_response

        keywords = ['test']
        search_type = 'Repositories'
        results = self.crawler.search_github(keywords, search_type)

        expected_url = 'https://github.com/test_owner/test_repo'
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], expected_url)

    @patch('app.main.GitHubCrawler.make_request')
    @patch('app.main.BeautifulSoup')
    def test_extract_repo_languages(self, mock_beautiful_soup, mock_make_request):
        mock_response = MagicMock()
        mock_make_request.return_value = mock_response

        mock_soup = MagicMock()
        mock_beautiful_soup.return_value = mock_soup
        mock_progress_item = MagicMock()
        mock_progress_item.get.return_value = 'Python 60.0%'
        mock_soup.find_all.return_value = [mock_progress_item]

        repo_url = 'https://github.com/test_owner/test_repo'
        languages = self.crawler.extract_repo_languages(repo_url)

        self.assertEqual(languages, {'Python': '60.0%'})
