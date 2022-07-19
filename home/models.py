from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, name=None):

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name):
        
        user = self.create_user(
            email=email,
            password=password,
            name=name,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user
        
class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length = 25)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def has_perm(self, perm, obj = None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    def __str__(self):
        return self.name +" => "+ self.email + " (Active: " + str(self.active) + ")"

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin
    
    @property
    def is_active(self):
        return self.active

class Team(models.Model):
    name = models.CharField(max_length = 50)
    country = models.CharField(max_length = 50, default="")
    in_the_bank = models.IntegerField(default = 5000000)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, null=True, blank=True)

def random_age():
    return random.randint(18, 40)

class Player(models.Model):
    position = ('goalkeeper', 'goalkeeper'), ('midfielder', 'midfielder'), ('defender', 'defender'), ('attacker', 'attacker')
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    player_position = models.CharField(choices = position, max_length = 15)
    country = models.CharField(max_length = 50, default="")
    age = models.IntegerField(default = random_age)
    market_value = models.IntegerField(default = 1000000)
    team = models.ForeignKey(Team, blank = True, null = True, on_delete=models.PROTECT)
    in_transfer = models.BooleanField(default = False)
    asking_price = models.IntegerField(default = 0)
