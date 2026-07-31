"""
Management command to create or update the admin user.
Usage: python manage.py setup_admin [username] [email] [password]
If no arguments provided, creates admin user with default credentials.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update the admin superuser'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Admin email (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(f"Admin user '{username}' already exists. Updating password...")
            )
            user.set_password(password)
            user.email = email
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Admin user '{username}' password updated successfully!")
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"Creating new admin user '{username}'...")
            )
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f"✓ Admin user '{username}' created successfully!")
            )
            self.stdout.write(f"   Username: {username}")
            self.stdout.write(f"   Email: {email}")
            self.stdout.write(f"   Password: {password}")
