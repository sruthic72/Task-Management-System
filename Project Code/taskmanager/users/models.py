from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    # Custom fields for your user model if any
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',  # Change related_name to a unique value
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Change related_name to a unique value
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    created_by = models.ForeignKey(User, related_name='reports', on_delete=models.CASCADE)

    def __str__(self):
        return f"Report {self.id} by {self.created_by.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Notification for {self.user.username} - {"Read" if self.is_read else "Unread"}'

    class Meta:
        ordering = ['-created_at']
