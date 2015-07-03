from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

import re
from django.template.defaultfilters import default

class UserManager(BaseUserManager):
 
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        
        if not username:
            raise ValueError(_('The given username must be set'))
        
        email = self.normalize_email(email)
        
        user = self.model(username=username, email=email,
             is_staff=is_staff, is_active=False,
             is_superuser=is_superuser, last_login=now,
             date_joined=now, **extra_fields)
        
        user.set_password(password)
        
        user.save(using=self._db)
        
        return user
 
    def create_user(self, username, email=None, password=None, **extra_fields):
        
        return self._create_user(username, email, password, False, False,
                 **extra_fields)
 
    def create_superuser(self, username, email, password, **extra_fields):
        
        user=self._create_user(username, email, password, True, True,
                 **extra_fields)
        
        user.is_active=True
        
        user.save(using=self._db)
        
        return user

class User(AbstractUser):
#     objects = UserManager()
#     """AbstractUser provides first_name, last_name, email, password. Use .get_full_name for first and last name"""
#     username = models.CharField(('username'), max_length=30, unique=True,
#     help_text=(''),
#     validators=[
#       validators.RegexValidator(re.compile('^[\w.@+-]+$'), ('Enter a valid username.'), ('invalid'))
#     ])
    is_student = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    # id_student = models.PositiveSmallIntegerField(unique=True, null=True)

class App(models.Model):
    id_app = models.PositiveSmallIntegerField()
    name_app = models.CharField(max_length=20)


class Exercise(models.Model):
    # id primary key
    fk_app = models.ForeignKey(App)
    id_exercise = models.PositiveSmallIntegerField()
    scoremax_possible = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('fk_app', 'id_exercise',)

    def __unicode__(self):
        exer_return = (str(self.id_exercise))
        return exer_return


class School(models.Model):
    # id primary key
    id_school = models.PositiveSmallIntegerField()


class Classroom(models.Model):
    # id primary key
    id_class = models.CharField(max_length=20)
    fk_school = models.ForeignKey(School)
    # users = models.ManyToManyField(User, related_name='classes')
    # student = models.ManyToManyField(Student, related_name='student')

    class Meta:
        unique_together = ('id_class', 'fk_school')


class Student(models.Model):
    # id
    id_student = models.PositiveSmallIntegerField()
    fk_class = models.ForeignKey(Classroom)


class Score(models.Model):
    # id primary key
    fk_exercise = models.ForeignKey(Exercise)
    fk_student = models.ForeignKey(Student)
    date = models.DateTimeField()
    score = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('fk_student', 'date', 'fk_exercise')

    def __unicode__(self):
        score_return = (str(self.student) + ' - ' + str(self.date) + ' - ' + str(self.exercise))
        return score_return

class Token(models.Model):
    
    hashed_token = models.TextField()
    used = models.BooleanField(default=False)