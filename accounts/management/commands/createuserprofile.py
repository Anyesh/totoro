from django.core.management.base import BaseCommand

from accounts.models import User
from accounts.views import create_user_profile


class Command(BaseCommand):
    help = "Check and create user profile"

    def create_profile(self):
        created_users = []
        users = User.objects.all()
        for user in users:
            status = create_user_profile(user)
            if status:
                self.stdout.write(
                    self.style.SUCCESS('Created profile for "%s"' % user.username)
                )
                created_users.append(user.username)

        return created_users

    def handle(self, *args, **options):
        users = self.create_profile()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created profile for "%s" users' % len(users)
            )
        )
