from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Repository, ReliabilityScore, ActivitySnapshot
from .forms import AddRepoForm
from .services.github_api import GitHubAPI
import plotly.graph_objs as go
from .services.score_calculator import ScoreCalculator


def index(request):
    repos = Repository.objects.all()

    repos_data = []
    for repo in repos:
        # Берём последнюю оценку для этого репозитория
        last_score = ReliabilityScore.objects.filter(repository=repo).last()
        total_score = last_score.total_score if last_score else None

        repos_data.append({
            'repo': repo,
            'score': total_score,
        })

    repos_data.sort(key=lambda x: x['score'] if x['score'] is not None else -1, reverse=True)

    return render(request, 'scorer_app/index.html', {'repos_data': repos_data})


def detail(request, repo_id):
    repo = get_object_or_404(Repository, id=repo_id)

    snapshots = ActivitySnapshot.objects.filter(repository=repo).order_by('snapshot_date')

    chart_dates = []
    chart_scores = []

    for s in snapshots:
        chart_dates.append(s.snapshot_date.strftime('%Y-%m-%d'))
        try:
            score_obj = ReliabilityScore.objects.get(snapshot=s)
            chart_scores.append(score_obj.total_score)
        except ReliabilityScore.DoesNotExist:
            continue

    # Проверяем, достаточно ли данных
    has_enough_data = len(chart_dates) >= 2

    # Строим график только если данных достаточно
    if has_enough_data:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_dates,
            y=chart_scores,
            mode='lines+markers',
            name='Оценка надежности',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8, color='#3b82f6')
        ))

        fig.update_layout(
            title='Динамика оценки надежности',
            xaxis_title='Дата',
            yaxis_title='Оценка (0-100)',
            yaxis=dict(range=[0, 110]),
            template='plotly_white',
            height=400,
            margin=dict(l=40, r=40, t=60, b=40),
        )

        graph_html = fig.to_html(full_html=False)
    else:
        graph_html = None

    # Текущая оценка
    last_score = ReliabilityScore.objects.filter(repository=repo).last()
    current_score = last_score.total_score if last_score else None

    context = {
        'repo': repo,
        'current_score': current_score,
        'graph_html': graph_html,
        'has_enough_data': has_enough_data,
    }
    return render(request, 'scorer_app/detail.html', context)


def add_repo(request):
    if request.method == 'POST':
        form = AddRepoForm(request.POST)
        if form.is_valid():
            repo = form.save(commit=False)

            # Получаем данные из GitHub API
            api = GitHubAPI()
            repo_data = api.get_repo_info(repo.full_name)

            if repo_data:
                # Заполняем данные из API
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

                # Создаём снимок
                snapshot = ActivitySnapshot.objects.create(
                    repository=repo,
                    commits_last_30_days=commits_count,
                    open_issues_count=issues_stats['open_issues_count'],
                    avg_issue_close_days=issues_stats['avg_issue_close_days'],
                    contributors_count=0,
                )

                # Считаем оценку
                scores = ScoreCalculator.calculate_total_score(
                    repo_data=repo_data,
                    commits_count=commits_count,
                    issues_stats=issues_stats,
                    contributors_count=0,
                )

                # Создаём оценку
                ReliabilityScore.objects.create(
                    repository=repo,
                    snapshot=snapshot,
                    total_score=scores['total_score'],
                    commit_score=scores['commit_score'],
                    issues_score=scores['issues_score'],
                    release_score=scores['release_score'],
                    community_score=scores['stars_score'],
                )

                messages.success(request, f'Репозиторий {repo.full_name} добавлен! Оценка: {scores["total_score"]}/100')
            else:
                # Если API не ответил, сохраняем без данных
                repo.save()
                messages.warning(request,
                                 f'Репозиторий {repo.full_name} добавлен, но не удалось получить данные из GitHub.')

            return redirect('detail', repo_id=repo.id)
    else:
        form = AddRepoForm()

    return render(request, 'scorer_app/add_repo.html', {'form': form})


def update_repo(request, repo_id):
    repo = get_object_or_404(Repository, id=repo_id)

    api = GitHubAPI()
    repo_data = api.get_repo_info(repo.full_name)

    if repo_data:
        # Обновляем данные репозитория
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

        # Создаём новый снимок
        snapshot = ActivitySnapshot.objects.create(
            repository=repo,
            commits_last_30_days=commits_count,
            open_issues_count=issues_stats['open_issues_count'],
            avg_issue_close_days=issues_stats['avg_issue_close_days'],
            contributors_count=0,
        )

        # Считаем оценку
        scores = ScoreCalculator.calculate_total_score(
            repo_data=repo_data,
            commits_count=commits_count,
            issues_stats=issues_stats,
            contributors_count=0,
        )

        # Создаём новую оценку
        ReliabilityScore.objects.create(
            repository=repo,
            snapshot=snapshot,
            total_score=scores['total_score'],
            commit_score=scores['commit_score'],
            issues_score=scores['issues_score'],
            release_score=scores['release_score'],
            community_score=scores['stars_score'],
        )

        messages.success(request, f'Данные обновлены! Новая оценка: {scores["total_score"]}/100')
    else:
        messages.warning(request, ' Не удалось обновить данные. GitHub API временно недоступно.')

    return redirect('detail', repo_id=repo.id)