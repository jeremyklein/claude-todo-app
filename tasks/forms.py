from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks with date picker"""

    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'status', 'priority',
                  'effort_points', 'due_date', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'effort_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control date-picker',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas'
            }),
        }
