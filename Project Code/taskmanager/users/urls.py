# users/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# from django.contrib.auth.decorators import login_required
from .views import RegisterView
from .views import LoginView, LogoutView, UserProfileView
from .views import TaskCreateView
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet
from .views import TaskAssignmentView
from .views import TaskStatusUpdateView
from .views import TaskDeleteView
from .views import UserTasksView
from .views import TaskUpdateView
from django.urls import include
from .views import DashboardView, ReportView
from .views import HomePageView, TaskDetailView
from . import views
from .views import UserListView, UserNotificationsView, NotificationReadView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('api/tasks/assign/<int:pk>/', TaskAssignmentView.as_view(), name='task-assign'),
    path('api/tasks/status/<int:pk>/', TaskStatusUpdateView.as_view(), name='task-status-update'),
    path('api/tasks/delete/<int:pk>/', TaskDeleteView.as_view(), name='task-delete'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/tasks/', UserTasksView.as_view(), name='user-tasks'),
    path('api/tasks/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/reports/', ReportView.as_view(), name='reports'),
    path('api/home/', HomePageView.as_view(), name='home'),
    path('api/tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('api/user-list/', UserListView.as_view(), name='user-list'),
    path('api/notifications/', UserNotificationsView.as_view(), name='user-notifications'),
    path('api/notifications/read/<int:pk>/', NotificationReadView.as_view(), name='notification-read'),
    path('app/', views.index, name='home_page'),
    path('app/login/', views.login, name='login_page'),
    path('app/register/', views.register, name='register_page'),
    path('app/tasks/', views.tasks, name='tasks_page'),
    path('app/dashboard/', views.dashboard, name='dashboard_page'),
    path('app/profile/', views.profile, name='profile_page'),
    path('app/add-task/', views.addTask, name='profile_page'),
    path('app/edit-task-status/<int:pk>/', views.edit_task_status, name='edit_task_status'),
    path('', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
