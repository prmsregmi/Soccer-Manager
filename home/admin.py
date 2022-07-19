from django.contrib import admin
from .models import CustomUser, Player, Team

admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Team)

# Register your models here.
