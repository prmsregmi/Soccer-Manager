from rest_framework import serializers
from .models import Team, Player
from django.db.models import Sum
from drf_yasg.utils import swagger_serializer_method

class TeamPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        exclude = ["team"]

class PlayerTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']

class PlayerSerializer(serializers.ModelSerializer):
    team = PlayerTeamSerializer()
    class Meta:
        model = Player
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name','country','in_the_bank', 'team_value', 'players']
    
    players = serializers.SerializerMethodField('get_players')
    team_value = serializers.SerializerMethodField('get_team_value')
    
    def get_team_value(self, obj):
        players = obj.player_set.all()
        team_value = players.aggregate(sum=Sum("market_value"))["sum"]
        return team_value
        
    @swagger_serializer_method(serializer_or_field=PlayerSerializer(many=True))
    def get_players(self, obj):
        players = obj.player_set.all()
        return TeamPlayerSerializer(players, many=True).data
