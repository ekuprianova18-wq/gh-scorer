import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class GitHubAPI:
    """
    Класс для работы с GitHub REST API
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):
        """
        Токен можно передать, чтобы было больше запросов
        Если токен не передан, пробуем взять из .env
        """
        self.session = requests.Session()

        if token is None:
            token = os.getenv('GITHUB_TOKEN')

        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github.v3+json'
            })

    def get_repo_info(self, repo_full_name):
        """
        Получаем основную информацию о репозитории
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            result = {
                'full_name': data['full_name'],
                'url': data['html_url'],
                'description': data.get('description', ''),
                'stars': data['stargazers_count'],
                'forks': data['forks_count'],
                'last_commit_date': self._get_last_commit_date(repo_full_name),
                'last_release_date': self._get_last_release_date(repo_full_name),
            }
            return result
        except requests.exceptions.RequestException:
            return None

    def _get_last_commit_date(self, repo_full_name):
        """
        Получаем дату последнего коммита
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/commits"

        try:
            response = self.session.get(url, params={'per_page': 1})
            commits = response.json()
            if commits:
                commit_date = commits[0]['commit']['committer']['date']
                return datetime.fromisoformat(commit_date.replace('Z', '+00:00')).date()
        except Exception:
            pass
        return None

    def _get_last_release_date(self, repo_full_name):
        """
        Получаем дату последнего релиза
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/releases"

        try:
            response = self.session.get(url, params={'per_page': 1})
            releases = response.json()
            if releases:
                release_date = releases[0]['published_at']
                return datetime.fromisoformat(release_date.replace('Z', '+00:00')).date()
        except Exception:
            pass
        return None

    def get_commits_count_last_30_days(self, repo_full_name):
        """
        Считаем, сколько было коммитов за последние 30 дней
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/commits"
        since_date = (datetime.now() - timedelta(days=30)).isoformat()

        try:
            response = self.session.get(url, params={'since': since_date, 'per_page': 100})
            commits = response.json()
            if isinstance(commits, list):
                return len(commits)
            return 0
        except Exception:
            return 0

    def get_issues_stats(self, repo_full_name):
        """
        Получаем статистику по issues
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/issues"

        try:
            response_open = self.session.get(url, params={'state': 'open', 'per_page': 1})
            open_issues = response_open.json()
            if isinstance(open_issues, list):
                open_count = len(open_issues)
            else:
                open_count = 0

            response_closed = self.session.get(url, params={'state': 'closed', 'per_page': 100})
            closed_issues = response_closed.json()

            avg_close_days = 0
            if isinstance(closed_issues, list) and closed_issues:
                total_days = 0
                count = 0
                for issue in closed_issues[:30]:
                    if issue.get('closed_at') and issue.get('created_at'):
                        closed_at = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                        created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                        days_open = (closed_at - created_at).days
                        if days_open > 0:
                            total_days += days_open
                            count += 1
                if count > 0:
                    avg_close_days = round(total_days / count, 1)

            return {
                'open_issues_count': open_count,
                'avg_issue_close_days': avg_close_days
            }
        except Exception:
            return {'open_issues_count': 0, 'avg_issue_close_days': 0}

    def get_contributors_count(self, repo_full_name):
        """
        Получаем количество контрибьюторов
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/contributors"

        try:
            response = self.session.get(url, params={'per_page': 100})
            contributors = response.json()
            if isinstance(contributors, list):
                return len(contributors)
            return 0
        except Exception:
            return 0