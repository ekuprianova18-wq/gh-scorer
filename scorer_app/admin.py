from django.contrib import admin
from .models import Repository, ActivitySnapshot, ReliabilityScore


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'stars', 'forks', 'updated_at']
    search_fields = ['full_name', 'description']
    list_filter = ['stars']


@admin.register(ActivitySnapshot)
class ActivitySnapshotAdmin(admin.ModelAdmin):
    list_display = ['repository', 'snapshot_date', 'commits_last_30_days', 'contributors_count']
    list_filter = ['snapshot_date']


@admin.register(ReliabilityScore)
class ReliabilityScoreAdmin(admin.ModelAdmin):
    list_display = ['repository', 'total_score', 'calculated_at']
    list_filter = ['total_score']