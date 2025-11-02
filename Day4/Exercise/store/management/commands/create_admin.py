from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = "Create or update admin superuser"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@techstore.com',
            help='Admin email (default: admin@techstore.com)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update password if user exists'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        force = options.get('force', False)

        # Check if user exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully created superuser: {username}'
                )
            )
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Password: {password}')
        else:
            if force:
                user.set_password(password)
                user.email = email
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully updated superuser: {username}'
                    )
                )
                self.stdout.write(f'   Email: {email}')
                self.stdout.write(f'   Password: {password}')
            else:
                if not user.is_staff or not user.is_superuser:
                    user.is_staff = True
                    user.is_superuser = True
                    user.email = email
                    user.save()
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  User {username} exists but was not a superuser.'
                        )
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Updated {username} to superuser status.'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  User {username} already exists as superuser.'
                        )
                    )
                    self.stdout.write(
                        self.style.NOTICE(
                            '   Use --force to reset the password.'
                        )
                    )

