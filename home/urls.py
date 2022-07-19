from django.urls import path
from .views import *

urlpatterns = [
    # API URLS ONLY
    path('', team_page, name="team_page"),
    path('transfer_list/', transfer_list, name="transfer_list")

    
]