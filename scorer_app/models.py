from django.db import models


class Repository(models.Model):
    """GitHub репозиторий"""
    full_name = models.CharField(max_length=200, unique=True, help_text="Например: django/django")
    url = models.URLField(help_text="https://github.com/owner/repo")
    description = models.TextField(blank=True)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    last_commit_date = models.DateField(null=True, blank=True)
    last_release_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class ActivitySnapshot(models.Model):
    """Снимок активности репозитория для расчета метрик"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_date = models.DateField(auto_now_add=True)
    commits_last_30_days = models.IntegerField(default=0)
    open_issues_count = models.IntegerField(default=0)
    avg_issue_close_days = models.FloatField(default=0)
    contributors_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-snapshot_date']

    def __str__(self):
        return f"{self.repository.full_name} - {self.snapshot_date}"


class ReliabilityScore(models.Model):
    """Оценка надежности репозитория"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='reliability_scores')
    snapshot = models.ForeignKey(ActivitySnapshot, on_delete=models.CASCADE)
    total_score = models.FloatField(default=0, help_text="Общая оценка 0-100")
    commit_score = models.FloatField(default=0)
    issues_score = models.FloatField(default=0)
    release_score = models.FloatField(default=0)
    community_score = models.FloatField(default=0)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.repository.full_name}: {self.total_score:.1f}/100"