from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3498db', help_text='Hex color code')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    effort_points = models.IntegerField(default=1, help_text='Estimated effort points (1-10)')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')

    # Future LLM integration fields
    llm_suggested = models.BooleanField(default=False, help_text='Task suggested by LLM')
    llm_automatable = models.BooleanField(default=False, help_text='Task can be automated by LLM')
    llm_metadata = models.JSONField(null=True, blank=True, help_text='Additional LLM-related data')

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title

    def mark_completed(self):
        """Mark task as completed and record completion time"""
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()

            # Create a TaskCompletion record for analytics
            TaskCompletion.objects.create(
                task=self,
                user=self.user,
                effort_points=self.effort_points,
                completed_at=self.completed_at
            )

    def get_priority_display_color(self):
        """Return a color based on priority for UI"""
        colors = {
            1: '#95a5a6',  # Low - Gray
            2: '#3498db',  # Medium - Blue
            3: '#f39c12',  # High - Orange
            4: '#e74c3c',  # Urgent - Red
        }
        return colors.get(self.priority, '#3498db')


class TaskCompletion(models.Model):
    """Track completed tasks for analytics and effort point tracking"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completions')
    effort_points = models.IntegerField()
    completed_at = models.DateTimeField()

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.task.title} - {self.effort_points} points"

    @classmethod
    def get_points_for_period(cls, user, start_date, end_date):
        """Get total effort points for a user in a given period"""
        return cls.objects.filter(
            user=user,
            completed_at__gte=start_date,
            completed_at__lt=end_date
        ).aggregate(total=Sum('effort_points'))['total'] or 0

    @classmethod
    def get_daily_points(cls, user, date=None):
        """Get points for a specific day"""
        if date is None:
            date = timezone.now().date()
        start = datetime.combine(date, datetime.min.time())
        end = start + timedelta(days=1)
        return cls.get_points_for_period(user, start, end)

    @classmethod
    def get_weekly_points(cls, user, date=None):
        """Get points for the current week"""
        if date is None:
            date = timezone.now().date()
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=7)
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())
        return cls.get_points_for_period(user, start, end)

    @classmethod
    def get_monthly_points(cls, user, date=None):
        """Get points for the current month"""
        if date is None:
            date = timezone.now().date()
        start = date.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())
        return cls.get_points_for_period(user, start, end)

    @classmethod
    def get_yearly_points(cls, user, date=None):
        """Get points for the current year"""
        if date is None:
            date = timezone.now().date()
        start = date.replace(month=1, day=1)
        end = start.replace(year=start.year + 1)
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())
        return cls.get_points_for_period(user, start, end)


class Note(models.Model):
    """Additional notes that can be attached to tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.task.title}"
