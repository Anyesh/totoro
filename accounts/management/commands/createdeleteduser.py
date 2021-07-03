from django.core.management.base import BaseCommand

from accounts.models import Profile, User


class Command(BaseCommand):
    help = "Creates deleted user"

    def create_user(self, password):
        deleted_user = User.objects.create(
            username="deleted_user", email="deleted@totoro.com"
        )
        deleted_user.set_password(password)
        deleted_user.save()
        Profile.objects.update_or_create(user=deleted_user)
        deleted_user.profile.save()
        return deleted_user

    def handle(self, *args, **options):
        password = None

        while not password:
            password = input("Password: ")
        try:
            deleted_user = User.objects.get(username="deleted_user")
            deleted_user.delete()
            usr = self.create_user(password)
        except Exception:
            usr = self.create_user(password)

        self.stdout.write(
            self.style.SUCCESS('Successfully created user "%s"' % usr.user_id)
        )
