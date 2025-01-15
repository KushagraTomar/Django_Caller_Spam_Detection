from django.contrib import admin
from users.models import CustomUser, RegisteredUserContact, ReportedUserSpam

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(RegisteredUserContact)
admin.site.register(ReportedUserSpam)