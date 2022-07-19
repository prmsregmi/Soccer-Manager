from random import random
from rest_framework.views import APIView
from rest_framework import status
from .serializers import PlayerSerializer, TeamSerializer
from .models import CustomUser, Player, Team
from django.contrib.auth import login as auth_login, authenticate
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
import names
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .countries import get_random_country, check_country_exists
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class LoginApi(APIView):
    @swagger_auto_schema(
        operation_summary="Login to View the team and perform actions like transfer and purchase.",
        tags=['Authentication'],
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the user')
        }),
        responses={200:openapi.Schema(type=openapi.TYPE_STRING, description='Token of the user'), 401:"Login UnSuccessful"}
        )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(email=email, password=password)
        if user:
            auth_login(request, user)
            token,_ = Token.objects.get_or_create(user=user)
            return Response({"user_token":token.key},status=status.HTTP_200_OK)
        else:
            return Response({"detail":"Login UnSuccessful"},status=status.HTTP_401_UNAUTHORIZED)

class SignupApi(APIView):
    def generate_random_team(self, name, country, user):
        players = {'goalkeeper': 3, 'defender': 6, 'midfielder': 6, 'attacker': 5}

        team = Team.objects.create(name=name, country=country, user=user)
        for key, val in players.items():
            for i in range(val):
                Player.objects.create(player_position=key, first_name=names.get_first_name(), last_name=names.get_last_name(), team=team, country=get_random_country())

    @swagger_auto_schema(
        operation_summary="SignUp in the Fantasy and one team will be generated for the user and assigned.",
        tags=['Authentication'],
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the user'),
            'team_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the Team'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country of the Team')
        }),
        responses={200:openapi.Schema(type=openapi.TYPE_STRING, description='Token of the user'), 409:"Email already exists", 400:"Invalid Email"}
        )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        team_name = request.data.get('team_name')
        country = request.data.get('country')

        try:
            validate_email(email)
        except ValidationError as e:
            return Response({"detail": "Invalid Email"},status=status.HTTP_400_BAD_REQUEST)

        if(not check_country_exists(country)):
            return Response({"detail": "Invalid Country. Country Does not Exist."},status=status.HTTP_400_BAD_REQUEST)
        
        if(password == None or len(password)<6):
            return Response({"detail": "Invalid Password."},status=status.HTTP_400_BAD_REQUEST)

        if(team_name == None or team_name == ""):
            return Response({"detail": "Team Name cannot be empty"},status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.create(email=email)
            user.set_password(password)
            user.save()
            token,_ = Token.objects.get_or_create(user=user)

            self.generate_random_team(team_name, country, user)
            return Response({'user_token':token.key},status=status.HTTP_200_OK)
                
        except IntegrityError as e:
            print(e)
            return Response({"detail": "Email already exists"},status=status.HTTP_409_CONFLICT)

class TeamPageApi(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TeamSerializer

    @swagger_auto_schema(
        operation_summary="Get Current Team Information of LoggedIn User, with the information of all players in the team.",
        tags=['Team'],
        responses={200:TeamSerializer, 404:"Transfer List Not Found"}
        )
    def get(self, request):
        instance = Team.objects.get(user = request.user)
        serializer = TeamSerializer(instance)
        return Response(serializer.data)

class TransferListApi(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerSerializer

    user_response = openapi.Response('Players in Transfer List', TeamSerializer)
    @swagger_auto_schema(
        tags=['Transfer Player'],
        operation_summary="Get all the Players in Transfer List.",
        responses={200:PlayerSerializer(many=True),404:"Transfer List Not Found"}
        )
    def get(self, request):
        instance = Player.objects.filter(in_transfer=True)
        serializer = PlayerSerializer(instance, many=True)
        return Response(serializer.data)

class EditTeamApi(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerSerializer

    @swagger_auto_schema(
        tags=['Team'],
        operation_summary="Update information of a team - team name and/or country.",
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='New Team Name'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='New Country Name')
            }),
        responses={200:openapi.Schema(type=openapi.TYPE_STRING, description="Team updated successfully"), 400:"Name/Country cannot be Empty" , 404:"No Such Team", 204: "Empty Request Data", 500:"Internal Server Error"}
        )
    def patch(self, request):
        try:
            instance = Team.objects.get(user=request.user)
        except:
            return Response("No Such Team", status=status.HTTP_404_NOT_FOUND)

        if(not "name" in request.data and "country" in request.data):
            return Response("Empty Request Data", status=status.HTTP_204_NO_CONTENT)
            

        if "name" in request.data:
            if(not request.data["name"] == None and len(request.data["name"])>0):
                instance.name = request.data["name"]
            else:
                return Response({"detail": "Name can't be empty."}, status=status.HTTP_400_BAD_REQUEST)
                
        if "country" in request.data:
            if(not request.data["country"] == None and check_country_exists(request.data["country"])):
                instance.country = request.data["country"]
            else:
                return Response({"detail": "Invalid Country. Country Does not Exist."},status=status.HTTP_400_BAD_REQUEST)
                
        instance.save()
        return Response("Team updated successfully", status=status.HTTP_200_OK)

class EditPlayerApi(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerSerializer

    @swagger_auto_schema(
        tags=['Player'],
        operation_summary="Update Player information - player name and/or country.",
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='New First Name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='New Last Name'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='New Country Name')
            }),
        responses={200:openapi.Schema(type=openapi.TYPE_STRING, description="Player updated successfully"), 404:"No Such Player"}
        )
    def patch(self, request, player_id):
        instance = Player.objects.get(id=player_id)
        team = Team.objects.get(user=request.user)
        if not instance.team == team:
            return Response("No Such Player", status=status.HTTP_404_NOT_FOUND)
        
        
        if(not "first_name" in request.data and not "last_name" in request.data and "country" in request.data):
            return Response("Empty Request Data", status=status.HTTP_204_NO_CONTENT)

        if "first_name" in request.data:
            if (not request.data["first_name"] == None and not request.data["first_name"] == ""):
                instance.first_name = request.data["first_name"]
            else:
                return Response({"detail": "First Name cannot be empty."},status=status.HTTP_400_BAD_REQUEST)
                
        if "last_name" in request.data:
            if (not request.data["last_name"] == None and not request.data["last_name"] == ""):
                instance.last_name = request.data["last_name"]
            else:
                return Response({"detail": "Last Name cannot be empty."},status=status.HTTP_400_BAD_REQUEST)
                
        if "country" in request.data:
            if (not request.data["country"] == None and check_country_exists(request.data["country"])):
                instance.country = request.data["country"]
            else:
                return Response({"detail": "Invalid Country. Country Does not Exist."},status=status.HTTP_400_BAD_REQUEST)
                
        instance.save()
        return Response("Player updated successfully", status=status.HTTP_200_OK)

class TransferPlayerApi(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerSerializer

    @swagger_auto_schema(
        tags=['Transfer Player'],
        operation_summary="Add a player within user's team to transfer list.",
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'asking_price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Asking Price of Player')
        }),
        responses={200:"Player sent on transfer list", 404:"No Such Player in the Team"}
        )
    def patch(self, request, player_id):
        try:
            team = Team.objects.get(user=request.user)
            instance = Player.objects.get(id = player_id, team = team, in_transfer = False)
        except:
            return Response("No Such (Transferable) Player in the Team", status=status.HTTP_404_NOT_FOUND)

        try:
            instance.asking_price = request.data["asking_price"]
            instance.in_transfer = True
            instance.save()
        except ValueError as e:
            return Response("Value Error. Invalid Asking Price.", status=status.HTTP_400_BAD_REQUEST)

        return Response("Player sent on transfer list", status=status.HTTP_200_OK)

class PurchasePlayerApi(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerSerializer

    @swagger_auto_schema(
        tags=['Transfer Player'],
        operation_summary="Purchase player who is available in the transfer list.",
        responses={200:"Player purchase successful", 404:"No Such Player in Transfer List", 405: "Cannot buy own player", 400: "Insufficient Balance"}
    )
    def patch(self, request, player_id):
        try:
            instance = Player.objects.get(id = player_id, in_transfer = True)
        except:
            return Response("No Such Player in Transfer List", status=status.HTTP_404_NOT_FOUND)

        team = Team.objects.get(user=request.user)
        if instance.team == team:
            return Response("Cannot buy own player", status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if team.in_the_bank < instance.asking_price:
            return Response("Insufficient Balance", status=status.HTTP_400_BAD_REQUEST)
 
        increment = random()
        instance.market_value += increment * instance.market_value
        instance.in_transfer = False
        instance.team.in_the_bank += instance.asking_price
        instance.team.save()
        instance.team = team

        team.in_the_bank -= instance.asking_price
        team.save()

        instance.asking_price = 0
        instance.save()
        return Response("Player purchase successful", status=status.HTTP_200_OK)