from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create default roles and permissions'

    def handle(self, *args, **kwargs):
        admin_permissions = [
            'add_task', 'change_task', 'delete_task', 'view_task',
            'add_user', 'change_user', 'delete_user', 'view_user',
        ]

        regular_permissions = [
            'add_task', 'change_task', 'view_task',
        ]

        admin_group, created = Group.objects.get_or_create(name='admin')
        for perm in admin_permissions:
            permission = Permission.objects.get(codename=perm)
            admin_group.permissions.add(permission)

        regular_group, created = Group.objects.get_or_create(name='regular')
        for perm in regular_permissions:
            permission = Permission.objects.get(codename=perm)
            regular_group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS('Roles and permissions created successfully.'))
