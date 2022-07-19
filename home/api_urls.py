from django.urls import path
from .api_functions import *

urlpatterns = [
    # API URLS ONLY
    path('login/', LoginApi.as_view(), name="login_api"),
    path('signup/', SignupApi.as_view(), name="signup_api"),
    path('team_page/', TeamPageApi.as_view()),
    path('transfer_list/', TransferListApi.as_view()),
    path('transfer_player/<slug:player_id>/', TransferPlayerApi.as_view(), name="transfer_player"),
    path('purchase_player/<slug:player_id>/', PurchasePlayerApi.as_view(), name="purchase_player"),
    path('edit_player/<slug:player_id>/', EditPlayerApi.as_view(), name="edit_player"),
    path('edit_team/', EditTeamApi.as_view(), name="edit_team"),
    
]