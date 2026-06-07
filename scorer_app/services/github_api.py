"""
GitHub API клиент для получения данных о репозиториях
"""

import requests
from datetime import datetime, timedelta

class GitHubAPI:
    """
    Класс для работы с GitHub REST API
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):
        """
        Токен можно передать, чтобы было больше запросов
        """
        self.session = requests.Session()
        if token:
            # Добавляем токен в заголовки, если он есть
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
            # Проверяем, что запрос успешный
            response.raise_for_status()
            data = response.json()

            result = {
                'full_name': data['full_name'],
                'url': data['html_url'],
                'description': data.get('description', ''),  # если нет описания — пустая строка
                'stars': data['stargazers_count'],
                'forks': data['forks_count'],
                'last_commit_date': self._get_last_commit_date(repo_full_name),
                'last_release_date': self._get_last_release_date(repo_full_name),
            }
            return result
        except requests.exceptions.RequestException as e:
            # Если что-то пошло не так - выводим ошибку и возвращаем None
            print(f"Не получилось получить данные для {repo_full_name}: {e}")
            return None

    def _get_last_commit_date(self, repo_full_name):
        """
        Получаем дату последнего коммита
        Берём только самый свежий коммит
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/commits"

        try:
            response = self.session.get(url, params={'per_page': 1})
            commits = response.json()
            if commits:
                # Достаём дату из ответа
                commit_date = commits[0]['commit']['committer']['date']
                # Приводим к формату даты (без времени)
                return datetime.fromisoformat(commit_date.replace('Z', '+00:00')).date()
        except Exception as e:
            # Если ошибка - просто пропускаем
            print(f"Не удалось получить дату коммита для {repo_full_name}: {e}")
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
        except Exception as e:
            print(f"Не удалось получить дату релиза для {repo_full_name}: {e}")
        return None

    def get_commits_count_last_30_days(self, repo_full_name):
        """
        Считаем, сколько было коммитов за последние 30 дней
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/commits"
        # Вычисляем дату 30 дней назад
        since_date = (datetime.now() - timedelta(days=30)).isoformat()

        try:
            response = self.session.get(url, params={'since': since_date, 'per_page': 100})
            commits = response.json()
            if isinstance(commits, list):
                return len(commits)
            return 0
        except:
            return 0

    def get_issues_stats(self, repo_full_name):
        """
        Получаем статистику по issues:
        сколько открытых issues
        среднее время закрытия (в днях)
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/issues"

        try:
            # Сначала получаем количество открытых issues
            response_open = self.session.get(url, params={'state': 'open', 'per_page': 1})
            open_issues = response_open.json()
            if isinstance(open_issues, list):
                open_count = len(open_issues)
            else:
                open_count = 0

            # Теперь считаем среднее время закрытия
            # Берём последние 100 закрытых issues
            response_closed = self.session.get(url, params={'state': 'closed', 'per_page': 100})
            closed_issues = response_closed.json()

            avg_close_days = 0
            if isinstance(closed_issues, list) and closed_issues:
                total_days = 0
                count = 0
                # Ограничимся 30 issues, чтобы не грузить API
                for issue in closed_issues[:30]:
                    if issue.get('closed_at') and issue.get('created_at'):
                        closed_at = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                        created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                        days_open = (closed_at - created_at).days
                        if days_open > 0:
                            total_days += days_open
                            count += 1
                if count > 0:
                    avg_close_days = round(total_days / count, 1)  # округляем до одного знака

            return {
                'open_issues_count': open_count,
                'avg_issue_close_days': avg_close_days
            }
        except Exception as e:
            print(f"Ошибка при получении issues для {repo_full_name}: {e}")
            return {'open_issues_count': 0, 'avg_issue_close_days': 0}

    def get_contributors_count(self, repo_full_name):
        """
        Получаем количество людей, которые вносили изменения
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}/contributors"

        try:
            # Пытаемся получить до 100 контрибьюторов
            response = self.session.get(url, params={'per_page': 100})
            contributors = response.json()
            if isinstance(contributors, list):
                return len(contributors)
            return 0
        except:
            return 0


# Небольшая проверка при запуске файла напрямую
if __name__ == "__main__":
    # Тестируем на одном репозитории
    api = GitHubAPI()
    info = api.get_repo_info("pandas-dev/pandas")
    if info:
        print(f"Репозиторий: {info['full_name']}")
        print(f"Звёзд: {info['stars']}")
        print(f"Форков: {info['forks']}")
    else:
        print("Не удалось получить данные")