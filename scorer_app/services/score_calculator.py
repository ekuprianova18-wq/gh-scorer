from datetime import date


class ScoreCalculator:
    """
    Рассчитывает надёжность репозитория по шкале 0-100.
    Формула:
    40% - активность коммитов
    30% - скорость закрытия issues
    20% - свежесть релизов
    10% - популярность (звёзды)
    """

    @staticmethod
    def calculate_total_score(repo_data, commits_count, issues_stats, contributors_count=None):
        """
        Главная функция расчёта.
        repo_data: словарь с ключами 'stars' и 'last_release_date'
        commits_count: число коммитов за 30 дней
        issues_stats: словарь с ключом 'avg_issue_close_days'
        """
        commit_points = ScoreCalculator._commits_points(commits_count)
        issues_points = ScoreCalculator._issues_points(issues_stats.get('avg_issue_close_days'))
        release_points = ScoreCalculator._release_points(repo_data.get('last_release_date'))
        stars_points = ScoreCalculator._stars_points(repo_data.get('stars', 0))

        total = commit_points + issues_points + release_points + stars_points

        return {
            'total_score': round(total, 1),
            'commit_score': round(commit_points, 1),
            'issues_score': round(issues_points, 1),
            'release_score': round(release_points, 1),
            'stars_score': round(stars_points, 1),
        }

    @staticmethod
    def _commits_points(commits_count):
        if commits_count >= 30:
            return 40
        elif commits_count <= 0:
            return 0
        else:
            return (commits_count / 30) * 40

    @staticmethod
    def _issues_points(avg_days):
        if avg_days is None or avg_days <= 0:
            return 5
        if avg_days <= 7:
            return 30
        elif avg_days <= 14:
            return 20
        elif avg_days <= 30:
            return 10
        else:
            return 5

    @staticmethod
    def _release_points(last_release_date):
        if last_release_date is None:
            return 0

        days_ago = (date.today() - last_release_date).days
        months_ago = days_ago / 30

        if months_ago <= 3:
            return 20
        elif months_ago <= 6:
            return 16
        elif months_ago <= 12:
            return 12
        elif months_ago <= 24:
            return 6
        else:
            return 0

    @staticmethod
    def _stars_points(stars):
        if stars >= 10000:
            return 10
        elif stars >= 5000:
            return 8
        elif stars >= 1000:
            return 5
        elif stars >= 100:
            return 2
        else:
            return 0