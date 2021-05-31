from django.contrib import admin

from accounts.models import Gender, Profile, Token, User

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Gender)

admin.site.register(Token)
