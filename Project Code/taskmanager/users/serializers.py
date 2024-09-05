from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import Task, Report, Notification

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User is deactivated.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
    
    def create(self, validated_data):
        # Assuming you want to use the request user as the creator
        # Remove any non-model field if it's being mistakenly passed here
        validated_data.pop('creator', None)  # Safe removal of an extraneous field
        
        # If 'creator' should be a field on Task, ensure the Task model has a `creator` field and it's a ForeignKey to User
        # If 'assigned_to' should automatically be the request user (common for creator scenarios):
        # user = self.context['request'].user
        # validated_data['assigned_to'] = user  # Only do this if business logic requires automatic assignment to the creator

        task = Task.objects.create(**validated_data)
        return task

class TaskAssignmentSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Task
        fields = ['assigned_to']

class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']
        extra_kwargs = {
            'status': {'required': True}
        }

class UserProfileSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'new_password', 'confirm_new_password', 'tasks']
        extra_kwargs = {'first_name': {'required': True}, 'last_name': {'required': True}}
    
    def validate(self, data):
        if 'new_password' in data and 'confirm_new_password' in data:
            if data['new_password'] != data['confirm_new_password']:
                raise serializers.ValidationError({"confirm_new_password": "Password fields didn't match."})
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        
        if 'new_password' in validated_data:
            instance.set_password(validated_data['new_password'])
        
        instance.save()
        return instance

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'assigned_to']

class DashboardSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    reports = serializers.ListField(child=serializers.DictField())

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'created_at', 'data', 'created_by']

class HomePageSerializer(serializers.Serializer):
    overview = serializers.DictField(child=serializers.CharField())
    tasks = TaskSerializer(many=True)

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at', 'task']
