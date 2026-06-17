from django.core.management.base import BaseCommand
from scorer_app.models import Repository, ActivitySnapshot, ReliabilityScore
from scorer_app.services.github_api import GitHubAPI
from scorer_app.services.score_calculator import ScoreCalculator


class Command(BaseCommand):
    help = 'Обновляет данные всех репозиториев через GitHub API'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю обновление...')

        api = GitHubAPI()
        repos = Repository.objects.all()
        self.stdout.write(f'Найдено репозиториев: {repos.count()}')

        for repo in repos:
            self.stdout.write(f'Обрабатываю: {repo.full_name}')

            # Получаем свежие данные из GitHub
            repo_data = api.get_repo_info(repo.full_name)
            if not repo_data:
                self.stdout.write(f'   Ошибка: не удалось получить данные')
                continue

            # Обновляем основную информацию о репозитории
            repo.stars = repo_data['stars']
            repo.forks = repo_data['forks']
            repo.description = repo_data['description']
            repo.last_commit_date = repo_data['last_commit_date']
            repo.last_release_date = repo_data['last_release_date']
            repo.save()

            # Получаем статистику
            commits_count = api.get_commits_count_last_30_days(repo.full_name)
            issues_stats = api.get_issues_stats(repo.full_name)
            issues_stats['closed_issues_count'] = issues_stats.get('open_issues_count', 0)

            # Создаем новый снимок
            snapshot = ActivitySnapshot.objects.create(
                repository=repo,
                commits_last_30_days=commits_count,
                open_issues_count=issues_stats['open_issues_count'],
                avg_issue_close_days=issues_stats['avg_issue_close_days'],
                contributors_count=0,
            )

            # Рассчитываем оценку
            scores = ScoreCalculator.calculate_total_score(
                repo_data=repo_data,
                commits_count=commits_count,
                issues_stats=issues_stats,
                contributors_count=0,
            )

            # Создаем новую оценку (привязываем к новому снимку)
            ReliabilityScore.objects.create(
                repository=repo,
                snapshot=snapshot,
                total_score=scores['total_score'],
                commit_score=scores['commit_score'],
                issues_score=scores['issues_score'],
                release_score=scores['release_score'],
                community_score=scores['stars_score'],
            )

            self.stdout.write(f'   Оценка: {scores["total_score"]}/100 (снимок {snapshot.snapshot_date})')

        self.stdout.write(' Готово')