from django.db import IntegrityError
from dashboard.models import Score, Exercise, App, User, School, Classroom, Student  # to use models
import csv  # for CSV parser
import sqlite3  # for DB
from .forms import UploadFileForm, ChooseClassForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.core.context_processors import csrf  # For form POST security CSRF token
from django.contrib import auth  #for authentication
from io import TextIOWrapper  #
from django.contrib.admin.views.decorators import staff_member_required



def index(request):
    context = RequestContext(request)
    context_dict = {'message': 'Login'}
    return render_to_response('dashboard/index.html', context_dict, context)


def dashboard(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    scores_list = Score.objects.order_by("date")
    class_list = Classroom.objects.values("id_class")
    scores_per_class = []
    for c in class_list:
        id = c['id_class']
        count = Score.objects.filter(fk_student__fk_class__id_class=id).count()
        # Score.objects.filter(Class=c).count()
        scores_per_class.append((id, count))

    # Query the database for a list of ALL students currently stored.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    # students_list = User.objects.exclude(id_student__isnull=True)
    students_list = Student.objects.order_by("id_student")
    exercises_list = Exercise.objects.order_by("fk_app__id_app")
    app_list = App.objects.values('name_app')
    context_dict = {"student": students_list, "exercise": exercises_list, "score": scores_list, "app_name": app_list,
        "scores_per_class": scores_per_class}

    return render_to_response('dashboard/dashboard.html', context_dict, context)


def usage(request):
    context = RequestContext(request)
    score_list = Score.objects.values_list('score', flat=True)
    c = Classroom.objects.all()
    date_list = Score.objects.filter(student__fk_class=c).date.month
    context_dict = {"score": score_list}

    '''for app in App
        {SELECT COUNT FROM dashboard_score WHERE strftime('%m','date')='02' AND score.exercise.id_app=app}'''

    return render_to_response('dashboard/usage.html', context_dict, context)


def scores(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    calc_count_list = []
    lire_count_list = []
    colordict = {'1': '#40af49', '2': '#ac558a', '3': '#f05541', '4': '#3ac2d0', '5': '#faaf3c', '6': '#4287b0'}
    # for a in id_app_list   # make list of lists to make number of charts dynamic
    calc_list = Exercise.objects.filter(fk_app__id_app=1).order_by("id_exercise")
    for cl in calc_list:
        sc = Score.objects.filter(fk_exercise__id_exercise=cl.id_exercise).count()
        calc_count_list.append((cl.id_exercise, sc, colordict[str(cl.id_exercise)]))

    lire_list = Exercise.objects.filter(fk_app__id_app=2).order_by("id_exercise")
    for ll in lire_list:
        sc = Score.objects.filter(fk_exercise__id_exercise=ll.id_exercise).count()
        lire_count_list.append((ll.id_exercise, sc, colordict[str(ll.id_exercise)]))

    # Query the database for a list of ALL students currently stored.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    scores_list = Score.objects.order_by("fk_exercise__id_exercise")
    # score_list = [s.score for s in Score.objects.all()]
    # {'score_list': [student_score.score for student_score in Score.objects.get(student__id=3)]}
    context_dict = {"score": scores_list, "c_scorecount": calc_count_list, "l_scorecount": lire_count_list}

    # Render the response and send it back!
    return render_to_response('dashboard/scores.html', context_dict, context)


@staff_member_required
def classes(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    args = {}
    args.update(csrf(request))
    #  When button is clicked method is POST so file is uploaded with request.FILES
    if request.method == 'POST':
        form = ChooseClassForm(request.POST)
        args['form'] = form

        cid = request.POST.get('class_id')
        # Query the database for a list of ALL students currently stored.
        # Place the list in our context_dict dictionary which will be passed to the template engine.
        students_list = Student.objects.order_by("id_student")
        class_list = Classroom.objects.values("id_class")

        args.update({"student": students_list, "class_list": class_list})

        if form.is_valid():

            return HttpResponseRedirect('classes')
    # First time on the page method is GET so form is rendered on class.html
    else:
        form = ChooseClassForm
        args['form'] = form
    return render_to_response('dashboard/class.html', args, context)


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
            handle_csv_upload(TextIOWrapper(request.FILES['file'].file, encoding='macroman'))
            # After handler inserts into database, redirect calls page to display data
            return HttpResponseRedirect('scores')
    # First time on the page method is GET so form is rendered on upload.html
    else:
        form = UploadFileForm()
        args['form'] = form
    return render_to_response('dashboard/upload.html', args, context)


def handle_csv_upload(csvfile):
    reader = csv.reader(csvfile)  # read the CSV file into a list of strings

    for row in reader:  # for each row from the CSV format the data to correct data type and insert into database
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
        print('1')
        # User.objects.get_or_create(id_student=int(row[2]), school=schoolOjb, id_class=row[4])
        # Stores primary key to use as foreign key in Score Insert
        # User.objects.get_or_create(id_student=int(row[2]))
        studObj = Student.objects.get_or_create(id_student=int(row[2]), fk_class=classObj)[0]
        print('1')
        # Gets Score obj with date, student, and exercise if exists or adds it if it doesn't
        s, _ = Score.objects.get_or_create(date=formatted_date, fk_student=studObj, fk_exercise=exerObj)
        #  Adds score to the Score obj
        print('1')
        print('Score obj', s)
        s.score = int(row[6])
        print('Results pre db', s.score)
        s.save()
        s = Score(id=s.id)
        print('Results from db', s.score)

    # Close the csv file, commit changes, and close the connection
    csvfile.close()


def format_date(date):
    # Converts cvs date 'dim jan 11 08:05:30 GMT 2015' to SQLite date format '2015-01-11 08:05:30.000'
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
def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login', c)


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



