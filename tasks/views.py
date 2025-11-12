from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .models import Task, Category, TaskCompletion, Note
from .forms import TaskForm


@login_required
def dashboard(request):
    """Main dashboard view showing task overview and effort points"""
    user = request.user
    today = timezone.now().date()

    # Get tasks
    tasks_todo = Task.objects.filter(user=user, status='todo').order_by('-priority', 'due_date')
    tasks_in_progress = Task.objects.filter(user=user, status='in_progress')
    tasks_completed_today = Task.objects.filter(
        user=user,
        status='completed',
        completed_at__date=today
    )

    # Get effort points statistics
    points_today = TaskCompletion.get_daily_points(user, today)
    points_week = TaskCompletion.get_weekly_points(user, today)
    points_month = TaskCompletion.get_monthly_points(user, today)
    points_year = TaskCompletion.get_yearly_points(user, today)

    # Get upcoming tasks (due in next 7 days)
    upcoming_deadline = today + timedelta(days=7)
    upcoming_tasks = Task.objects.filter(
        user=user,
        status__in=['todo', 'in_progress'],
        due_date__gte=today,
        due_date__lte=upcoming_deadline
    ).order_by('due_date')

    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        user=user,
        status__in=['todo', 'in_progress'],
        due_date__lt=today
    ).order_by('due_date')

    # Get category stats
    category_stats = Category.objects.filter(
        tasks__user=user
    ).annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='completed'))
    ).order_by('-total_tasks')

    context = {
        'tasks_todo': tasks_todo[:5],  # Show top 5
        'tasks_in_progress': tasks_in_progress,
        'tasks_completed_today': tasks_completed_today,
        'points_today': points_today,
        'points_week': points_week,
        'points_month': points_month,
        'points_year': points_year,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        'category_stats': category_stats,
    }
    return render(request, 'tasks/dashboard.html', context)


class TaskListView(LoginRequiredMixin, ListView):
    """List all tasks for the current user"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """View a single task"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.all()
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create a new task"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing task"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a task"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


@login_required
def task_complete(request, pk):
    """Mark a task as completed"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.mark_completed()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def analytics(request):
    """Analytics view showing effort points over time"""
    user = request.user
    today = timezone.now().date()

    # Get daily points for the last 30 days
    daily_points = []
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        points = TaskCompletion.get_daily_points(user, date)
        daily_points.append({
            'date': date.strftime('%m/%d'),
            'points': points
        })

    # Get weekly points for the last 12 weeks
    weekly_points = []
    for i in range(11, -1, -1):
        date = today - timedelta(weeks=i)
        points = TaskCompletion.get_weekly_points(user, date)
        week_start = date - timedelta(days=date.weekday())
        weekly_points.append({
            'week': week_start.strftime('%m/%d'),
            'points': points
        })

    # Get monthly points for the last 12 months
    monthly_points = []
    for i in range(11, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        date = today.replace(year=year, month=month, day=1)
        points = TaskCompletion.get_monthly_points(user, date)
        monthly_points.append({
            'month': date.strftime('%b %Y'),
            'points': points
        })

    # Get category breakdown
    category_breakdown = TaskCompletion.objects.filter(
        user=user
    ).values(
        'task__category__name'
    ).annotate(
        total_points=Sum('effort_points'),
        task_count=Count('id')
    ).order_by('-total_points')

    # Get recent completions
    recent_completions = TaskCompletion.objects.filter(
        user=user
    ).select_related('task', 'task__category')[:10]

    # Overall stats
    total_tasks_completed = TaskCompletion.objects.filter(user=user).count()
    total_points_earned = TaskCompletion.objects.filter(
        user=user
    ).aggregate(Sum('effort_points'))['effort_points__sum'] or 0

    context = {
        'daily_points': daily_points,
        'weekly_points': weekly_points,
        'monthly_points': monthly_points,
        'category_breakdown': category_breakdown,
        'recent_completions': recent_completions,
        'total_tasks_completed': total_tasks_completed,
        'total_points_earned': total_points_earned,
    }
    return render(request, 'tasks/analytics.html', context)


@login_required
def add_note(request, task_pk):
    """Add a note to a task"""
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Note.objects.create(
                task=task,
                user=request.user,
                content=content
            )
    return redirect('task_detail', pk=task_pk)
