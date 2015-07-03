#coding: utf-8

from django.db.models import Avg, Count
from django.core.urlresolvers import reverse 
from dashboard.models import Score, Exercise, App, User, School, Classroom, Student, Token  # to use models
import csv  # for CSV parser
import sqlite3  # for DB
from django.contrib import messages
from .forms import UploadFileForm, ChooseClassForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, RequestContext
from django.core.context_processors import csrf  # For form POST security CSRF token
from django.contrib import auth  #for authentication
from io import TextIOWrapper  #
from django.db import IntegrityError, connection
from dashboard.forms import UserForm
from dashboard.forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import string, random, hashlib #For Token generation
#from dashboard.forms import MyRegistrationForm

def index(request):
    context = RequestContext(request)
    context_dict = {'message': 'Login'}
    return render_to_response('dashboard/index.html', context_dict, context)

def dashboard(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # decimal month for postgresql monthnum, two digit string from sqlite
    monthdict = {#sqlite
                 '01': 'Jan',
                 '02': 'Feb',
                 '03': 'Mar',
                 '04': 'Apr',
                 '05': 'May',
                 '06': 'Jun',
                 '07': 'Jul',
                 '08': 'Aug',
                 '09': 'Sep',
                 '10': 'Oct',
                 '11': 'Nov',
                 '12': 'Dec',
                 #postgresql
                 1.0: 'Jan',
                 2.0: 'Feb',
                 3.0: 'Mar',
                 4.0: 'Apr',
                 5.0: 'May',
                 6.0: 'Jun',
                 7.0: 'Jul',
                 8.0: 'Aug',
                 9.0: 'Sep',
                 10.0: 'Oct',
                 11.0: 'Nov',
                 12.0: 'Dec'
    }

    app_list = App.objects.values('name_app')
    app_count = App.objects.count()
    
    class_list = Classroom.objects.values("id_class")
    class_count = Classroom.objects.count()
    
    student_count = Student.objects.count()
    
    math_score_obj = Score.objects.filter(fk_exercise__fk_app__id_app=1)
    read_score_obj = Score.objects.filter(fk_exercise__fk_app__id_app=2)
    
    math_avg = math_score_obj.aggregate(Avg('score'))
    read_avg = read_score_obj.aggregate(Avg('score'))
    
    math_avg['score__avg'] = float("%.2f" %(math_avg['score__avg']))
    read_avg['score__avg'] = float("%.2f" %(read_avg['score__avg']))

    scores_per_class = []
    
    for c in class_list:
        id = c['id_class']
        count = Score.objects.filter(fk_student__fk_class__id_class=id).count()
        # Score.objects.filter(Class=c).count()
        scores_per_class.append((id, count))

    # IF checks database type to match up correct select statement
    if connection.vendor == 'sqlite':
        selectyear = 'strftime("%Y", date)'
        selectmonth = 'strftime("%m", date)'
    elif connection.vendor == 'postgresql':
        selectyear = 'extract( year from date )'
        selectmonth = 'extract( month from date )'
    # adds a year, month and total column to math_score_obj as ms queryset
    ms = math_score_obj.extra(select={'year': selectyear, 'month': selectmonth})\
        .annotate(total=Count('score')).order_by('year', 'month')
    # groups ms queryset by year and month
    ms.query.group_by = ['year', 'month']
    # returns list of totals for each year and month
    scorecount_month = ms.values('total', 'year', 'month')

    for sc in scorecount_month:
        monthnum = sc['month']
        sc['month'] = monthdict[monthnum]

    # Query the database for a list of ALL students currently stored.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    students_list = Student.objects.order_by("id_student")
    exercises_list = Exercise.objects.values('id_exercise', 'scoremax_possible', 'fk_app__name_app')\
        .order_by("fk_app__id_app")
    exercises_list = list(exercises_list)

    context_dict = {"student": students_list,
                    "student_count": student_count,
                    "exercise": exercises_list,
                    "app_name": app_list,
                    "app_count": app_count,
                    "class_count": class_count,
                    "scorecount_month": scorecount_month,
                    "scores_per_class": scores_per_class,
                    "math_avg": math_avg,
                    "read_avg": read_avg,
                    "title": 'Dashboard'
    }

    return render_to_response('dashboard/dashboard.html', context_dict, context)

def usage(request):
    context = RequestContext(request)

    calc_count_list = []
    lire_count_list = []
    
    colordict = {'1': '#40af49', '2': '#ac558a', '3': '#f05541', '4': '#3ac2d0', '5': '#faaf3c', '6': '#4287b0'}

    # make list of lists to make number of charts dynamic
    calc_list = Exercise.objects.filter(fk_app__id_app=1).order_by("id_exercise")
    for cl in calc_list:
        sc = Score.objects.filter(fk_exercise__id_exercise=cl.id_exercise, fk_exercise__fk_app__id_app=1).count()
        calc_count_list.append((cl.id_exercise, sc, colordict[str(cl.id_exercise)]))

    lire_list = Exercise.objects.filter(fk_app__id_app=2).order_by("id_exercise")
    for ll in lire_list:
        sc = Score.objects.filter(fk_exercise__id_exercise=ll.id_exercise, fk_exercise__fk_app__id_app=2).count()
        lire_count_list.append((ll.id_exercise, sc, colordict[str(ll.id_exercise)]))

    score_list = Score.objects.values_list('score', flat=True)
    class_list = Classroom.objects.all()
    score_month = []
    
    for c in class_list:
        score_ojb_list = Score.objects.filter(fk_student__fk_class=c)
        
        for s in score_ojb_list:
            score_month.append(s.date.month)
    
    context_dict = {"score": score_list,
                    "c_scorecount": calc_count_list,
                    "l_scorecount": lire_count_list,
                    "title": 'Usage',
                    "score_month": score_month
    }

    '''for app in App
        {SELECT COUNT FROM dashboard_score WHERE strftime('%m','date')='02' AND score.exercise.id_app=app}'''

    return render_to_response('dashboard/usage.html', context_dict, context)

def logs(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # Query the database for a list of ALL students currently stored.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    scores_list = Score.objects.order_by("fk_exercise__id_exercise")
    
    # score_list = [s.score for s in Score.objects.all()]
    # {'score_list': [student_score.score for student_score in Score.objects.get(student__id=3)]}
    context_dict = {"score": scores_list,
                    "title": 'Logs'
    }

    # Render the response and send it back!
    return render_to_response('dashboard/logs.html', context_dict, context)

#@staff_member_required
def classes(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    context_dict = {}
    
    # When button is clicked method is POST. The class ID is passed from form by request.POST
    if request.method == 'POST':
        form = ChooseClassForm(request.POST)
        context_dict['form'] = form

        cid = request.POST.get('class_id')
        
        # Query the database for a list of ALL students currently stored.
        # Place the list in our context_dict dictionary which will be passed to the template engine.
        students_list = Student.objects.filter(fk_class__id_class=cid).order_by("id_student")

        context_dict.update({"students": students_list,
                             "title": 'Classes',
                             "visibility": 'visible'
        })

        if form.is_valid():

            return render_to_response('dashboard/classes.html', context_dict, context)
    
    # First time on the page method is GET so form is rendered on classes.html
    else:
        form = ChooseClassForm
        # context_dict['form'] = form
        context_dict.update({"form": form,
                             "title": 'Classes',
                             "visibility": 'hidden'
        })
    
    return render_to_response('dashboard/classes.html', context_dict, context)

#@staff_member_required
def display_student_score(request, student_id):
    # Obtain the context from the HTTP request.

    scores_list = Score.objects.filter(fk_student_id=student_id).values('score', 'fk_exercise__scoremax_possible',
                                    'date', 'fk_exercise__id_exercise',
                                    'fk_exercise__fk_app__name_app').order_by('fk_exercise__id_exercise', '-date')
    scores_list = list(scores_list)
    studname = Student.objects.filter(id=student_id).values('id_student')
    studname = list(studname)
    context_dict = {}
    context_dict.update({"title": 'Classes', "scores": scores_list, "studname": studname})

    return JsonResponse(context_dict)

def upload_file(request):
    context = RequestContext(request)
    args = {}
    args.update(csrf(request))
    #  When button is clicked method is POST so file is uploaded with request.FILES
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        args['form'] = form
        if form.is_valid():
            # File is formatted Byte so is wrapped as utf-8 and passed to handler
            uploadCount = handle_csv_upload(TextIOWrapper(request.FILES['file'].file, encoding='macroman'))
            # After handler inserts into database, redirect calls page to display data
            args.update({"title": 'Upload', "uploadSuccess": True, "uploadCount": uploadCount})
            return render_to_response('dashboard/upload.html', args, context)
            # return HttpResponseRedirect('scores')
    # First time on the page method is GET so form is rendered on upload.html
    else:
        form = UploadFileForm()
        args['form'] = form
        args.update({"title": 'Upload', "uploadSuccess": False})
    return render_to_response('dashboard/upload.html', args, context)

def handle_csv_upload(csvfile):
    reader = csv.reader(csvfile)  # read the CSV file into a list of strings
    count = 0

    for row in reader:  
        # for each row from the CSV format the data to correct data type and insert into database
        # 0 = id_app, 1 = date, 2 = id_student, 3 = id_school, 4 = id_class,
        # 5 = id_exercise, 6 = score, 7 = scoremax_possible
        formatted_date = format_date(row[1])

        # .get_or_create creates a new object if it does not exist but it does not return the object
        # use .get to retrieve the ojbect to pass as foreign key
        appObj = App.objects.get(id_app=int(row[0]))

        exerObj = Exercise.objects.get_or_create(fk_app=appObj, id_exercise=int(row[5]),
                                            scoremax_possible=int(row[7]))[0]

        schoolObj = School.objects.get_or_create(id_school=int(row[3]))[0]

        classObj = Classroom.objects.get_or_create(id_class=row[4], fk_school=schoolObj)[0]

        # User.objects.get_or_create(id_student=int(row[2]), school=schoolOjb, id_class=row[4])
        # Stores primary key to use as foreign key in Score Insert
        # User.objects.get_or_create(id_student=int(row[2]))
        studObj = Student.objects.get_or_create(id_student=int(row[2]), fk_class=classObj)[0]
        # Gets Score obj with date, student, and exercise if exists or adds it if it doesn't
        try:
            s, created = Score.objects.get_or_create(date=formatted_date, fk_student=studObj, fk_exercise=exerObj,
                                                     score=(int(row[6])))
            if created:
                count += 1
        except IntegrityError:
            Score.objects.filter(date=formatted_date, fk_student=studObj, fk_exercise=exerObj).update(score=(int(row[6])))
    # Close the csv file, commit changes, and close the connection
    csvfile.close()
    return count

def format_date(date):
    # Converts cvs date 'dim jan 11 08:05:30 GMT 2015' to database date format '2015-01-11 08:05:30.000'
    upper_date = date.upper()
    date_list = upper_date.split()
    month = monthToNum(date_list[1])
    formatted_date = '{}-{}-{} {}.000'.format(date_list[5], month, date_list[2], date_list[3])
    return formatted_date

def monthToNum(date):  # Def to convert month abbreviation to a number

    return{
        'JAN': '01',  # For English
        'FEB': '02',
        'MAR': '03',
        'APR': '04',
        'MAY': '05',
        'JUN': '06',
        'JUL': '07',
        'AUG': '08',
        'SEP': '09',
        'OCT': '10',
        'NOV': '11',
        'DEC': '12',
        'FÉV': '02',  # For French
        'AVR': '04',
        'MAI': '05',
        'AOÛ': '08',
    }[date]


# authentication

def login(request, user):
    auth.login(request, user)

def login_user(request):
    context = RequestContext(request)
    logout(request)
    
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/dashboard/dashboard')
            else:
                HttpResponse("Your account is disabled")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render_to_response("dashboard/login.html", {}, context)
    
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        HttpResponseRedirect('accounts/loggedin.html')
    else:
        HttpResponseRedirect('accounts/invalid.html')

def loggedin(request):
    return render_to_response('loggedin.html',
        {'full_name': request.user.username})

def invalid_login(request):
    return render_to_response('invalid_login.html')

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')

def request_token(request):
    #TODO
    #Email handling, needs to be discussed
    print()
    
def generate_token(request):
    
    if(request.method == 'POST'):
        token = generate_a_token()
    
        messages.success(request, "Token generated with success!, you can now email it to the user. %s" %token, extra_tags="sticky")
        
    return render_to_response('generate_token.html', {'title':'Generate Token'}, context_instance=RequestContext(request))
    
        
def generate_a_token():
    #Generates and shuffles a string with digits and letters 
    chars = (string.ascii_letters + string.digits)
    charlist = list(chars)
    random.shuffle(charlist)
    chars = "".join(charlist)
    
    
    while(True):
        token = ""
    
        for i in range(5):
            token += (random.choice(chars))
            
        token = token.encode('utf-8')
        hash_token = (hashlib.sha512(token)).hexdigest()
        
        existing_token = False
        
        for i in Token.objects.all():
            if(hash_token == i.hashed_token):
                existing_token = True
                break
        
        if not (existing_token):
            Token.objects.create(hashed_token=hash_token)
            return token
    
def register(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        
        if form.is_valid():
            user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password2'])
            user.save()
#             user = form.save()
#             user.set_password(user.password)
#             user.save()
            
            return render_to_response("register_success.html")
    else:
        form = CreateUserForm(auto_id=False)
        
        return render_to_response('register.html', {
    'form': form,
},context_instance=RequestContext(request))
 
def register_user(request):
    if(request.method == 'POST'):
        form = UserForm(request.POST)
         
        if(form.is_valid()):
            form.save()
            return HttpResponseRedirect('/dashboard/accounts/register_success')
         
    args = {}
    args.update(csrf(request))
     
    args['form'] = UserForm()
     
    return render_to_response('register.html', args)

def register_success(request):
    HttpResponseRedirect('register_success.html')