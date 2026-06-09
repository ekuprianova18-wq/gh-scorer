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
    def calculate_total_score(repo_data, commits_count, issues_stats):
        """
        Главная функция расчёта.
        repo_data: словарь с ключами 'stars' и 'last_release_date'
        commits_count: число коммитов за 30 дней
        issues_stats: словарь с ключом 'avg_issue_close_days'
        """
        # Считаем каждый показатель
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

    # Оценка за коммиты
    @staticmethod
    def _commits_points(commits_count):
        if commits_count >= 30:
            return 40
        elif commits_count <= 0:
            return 0
        else:
            return (commits_count / 30) * 40

    # Оценка за ISSUES
    @staticmethod
    def _issues_points(avg_days):
        # Если нет данных
        if avg_days is None or avg_days <= 0:
            return 5
        # Если есть данные
        if avg_days <= 7:
            return 30
        elif avg_days <= 14:
            return 20
        elif avg_days <= 30:
            return 10
        else:
            return 5

    # Оценка за релизы (максимум 20 баллов)
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

    # Оценка за звезды (максимум 10 баллов)
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


# Тест
if __name__ == "__main__":
    print("Тест калькулятора:")
    print("-" * 30)

    # Хороший проект
    good_repo = {
        'stars': 50000,
        'last_release_date': date(2026, 5, 1)
    }
    result1 = ScoreCalculator.calculate_total_score(
        repo_data=good_repo,
        commits_count=25,
        issues_stats={'avg_issue_close_days': 10}
    )
    print(f"Хороший проект: {result1['total_score']}/100")

    # Плохой проект
    bad_repo = {
        'stars': 50,
        'last_release_date': date(2020, 1, 1)
    }
    result2 = ScoreCalculator.calculate_total_score(
        repo_data=bad_repo,
        commits_count=0,
        issues_stats={'avg_issue_close_days': None}
    )
    print(f"Плохой проект: {result2['total_score']}/100")