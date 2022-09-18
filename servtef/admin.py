from django.contrib import admin
from django.contrib.auth.models import User, Group


class UserAdmin(admin.ModelAdmin):
    model = User

    fields = ["username", "password", "email"]


#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


