from django.contrib import admin
from shoppingline.users import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["phone_number", "name", "twilio_worker_sid"]
    readonly_fields = ["last_login"]
