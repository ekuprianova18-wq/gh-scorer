from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Repository, ReliabilityScore


def index(request):
    repos = Repository.objects.all()

    repos_data = []
    for repo in repos:
        try:
            score_obj = repo.reliability_score
            total_score = score_obj.total_score
        except ReliabilityScore.DoesNotExist:
            total_score = None

        repos_data.append({
            'repo': repo,
            'score': total_score,
        })

    repos_data.sort(key=lambda x: x['score'] if x['score'] is not None else -1, reverse=True)

    return render(request, 'scorer_app/index.html', {'repos_data': repos_data})