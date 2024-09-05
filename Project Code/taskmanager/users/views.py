from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin, IsRegularUser
from .models import Task, Report
from .serializers import TaskSerializer, TaskAssignmentSerializer, TaskStatusUpdateSerializer, TaskUpdateSerializer
from .serializers import UserProfileSerializer, UserListSerializer
from .serializers import DashboardSerializer, ReportSerializer
from .serializers import HomePageSerializer
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from .models import Notification
from .serializers import NotificationSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super(RegisterView, self).create(request, *args, **kwargs)
        # Check if the user was created successfully
        if response.status_code == status.HTTP_201_CREATED:
            return redirect(reverse('login_page'))
        return response

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        # # print("Request object: ", request)
        # print("Request.post object: ", request.POST)
        if serializer.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            myuser = authenticate(request, username=username, password=password)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            if myuser is not None:
                auth.login(request, myuser)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            
            # print("myuser is None")
            # # login(request)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            auth.logout(request)
            return Response(status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsRegularUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='admin').exists():
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(creator=self.request.user)
        Notification.objects.create(
            user=instance.assigned_to,
            message=f'You have been assigned a new task: {instance.title}',
            task=instance
        )

class TaskAssignmentView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskStatusUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDeleteView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        total_tasks = Task.objects.filter(assigned_to=user).count()
        completed_tasks = Task.objects.filter(assigned_to=user, status='Completed').count()
        pending_tasks = Task.objects.filter(assigned_to=user, status='Pending').count()
        in_progress_tasks = Task.objects.filter(assigned_to=user, status='In Progress').count()

        reports = Report.objects.filter(created_by=user)
        report_data = [
            {"name": f"Report {report.id}", "data": report.data} for report in reports
        ]

        data = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "reports": report_data
        }

        serializer = DashboardSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()
        
        tasks = Task.objects.filter(assigned_to=user)
        completed_tasks = tasks.filter(status='Completed').count()
        pending_tasks = tasks.filter(status='Pending').count()
        in_progress_tasks = tasks.filter(status='In Progress').count()

        report_data = {
            "total_tasks": tasks.count(),
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "task_details": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat()  # Convert datetime to string
                } for task in tasks
            ]
        }

        report = Report.objects.create(data=report_data, created_by=user)
        
        if report:
            serializer = ReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'No reports found'}, status=status.HTTP_404_NOT_FOUND)

class HomePageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        overview_data = {
            "total_tasks": Task.objects.filter(assigned_to=user).count(),
            "completed_tasks": Task.objects.filter(assigned_to=user, status='Completed').count(),
            "pending_tasks": Task.objects.filter(assigned_to=user, status='Pending').count(),
            "in_progress_tasks": Task.objects.filter(assigned_to=user, status='In Progress').count(),
        }

        # Retrieve tasks assigned to the user
        tasks = Task.objects.filter(assigned_to=user)

        data = {
            "overview": overview_data,
            "tasks": list(tasks),  # Convert QuerySet to list
        }

        serializer = HomePageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assigned_to=user)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    # permission_classes = [IsAdminUser]  # Ensuring only admins can access user list

    def get_queryset(self):
        # queryset = self.queryset
        # username = self.request.query_params.get('username', None)
        # if username is not None:
        #     queryset = queryset.filter(username__icontains=username)
        # return queryset
        
        return super().get_queryset()

class UserNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')

class NotificationReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification read'})

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

@login_required(login_url='/app/login/')
def tasks(request):
    return render(request, 'tasks.html')

@login_required(login_url='/app/login/')
def dashboard(request):
    print("User: ", request.user)
    print("Authenticated: ", request.user.is_authenticated)
    return render(request, 'dashboard.html')

@login_required(login_url='/app/login/')
def profile(request):
    return render(request, 'profile.html')

@login_required(login_url='/app/login/')
def addTask(request):
    return render(request, 'addTask.html')

@login_required(login_url='/app/login/')
def edit_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'edit_task_status.html', {'task': task})
