from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import re
from django.template.defaultfilters import default



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
    role = models.CharField(max_length=20, default='')
    class_id = models.CharField(max_length=5, default='*')
    school_id = models.CharField(max_length=5, default='')

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
    name_school = models.CharField(max_length=200, default='')
    city_school = models.CharField(max_length=200, default='')
    number_students = models.PositiveIntegerField(default=0)
    number_classes = models.PositiveIntegerField(default=0)

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
        score_return = (str(self.fk_student) + ' - ' + str(self.date) + ' - ' + str(self.fk_exercise))
        return score_return

class Token(models.Model):
    
    hashed_token = models.TextField()
    used = models.BooleanField(default=False)
    user_role = models.CharField(max_length=20, default='')
    class_id = models.CharField(max_length=5, default='*')
    school_id = models.CharField(max_length=5, default='')