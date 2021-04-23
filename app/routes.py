from flask import render_template, request, redirect, url_for, session, flash
from app.models import User, Subscription, Trainer, Course
from app import app, db
from app.forms import UserForm, CourseForm, TrainerForm, SubscriptionForm, LoginForm, SearchForm
from datetime import datetime
import math
from helpers import navs, search
import functools


def login_required(view_func):
    @functools.wraps(view_func)
    def check_permissions(*args, **kwargs):
        if session.get('logged_in'):
            return view_func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))

    return check_permissions



@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = None
    next_url = request.args.get('next')
    search_form = SearchForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            errors = form.errors
    return render_template("login.html", form=form, errors=errors, navs=navs, search_form=search_form)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        flash("You are now logged out.", 'success')
    return redirect(url_for('index'))


@app.route('/', methods=["GET", "POST"])
def index():
    route = "/"
    search_form = SearchForm()
    data = [("Uczestnicy", "Zarządzaj listą uczestników - dodawaj nowych abonentów, edytuj lub usuwaj dane.",
             "static/pics/gra_6.jpg", "/users/0", ),
            ("Trenerzy", 'Tu wprowadzisz nowego pracownika a także edytujesz i usuniesz już istniejących.',
             "static/pics/gra_11.jpg", "/trainers/0"),
            ("Zajęcia", 'Przejdż do listy zajęć. Dodaj nowe zajęcia lub usuń te, które nie są już aktualne.',
             "static/pics/tra_back.jpg", "/courses/0"),
            ("Abonamenty", 'Sprawdź typy abonamentów oferowanych przez klub i w razie potrzeby stwórz nowe.',
             "static/pics/ba_sub.jpg", "/subscriptions/0")]
    if request.method == "POST":
        if search_form.data["name"] != '':
            return search()
        else:
            pass

    return render_template("home.html", data=data, navs=navs, route=route, search_form=search_form)


@app.route('/users/<int:num>', methods=["GET", "POST"])
@login_required
def users_all(num):
    search_form = SearchForm()
    route = "/users/0"
    users = User.query.all()[num*4:num*4+4]
    users_num = math.ceil((len(User.query.all()))/4)
    new_id = max([user.id for user in User.query.all()]) + 1
    trainers = Trainer.query.all()
    subscriptions = Subscription.query.all()
    form = UserForm()
    error = None
    if request.method == "POST":
        name = form.data["name"]
        active = form.data["active"]
        subscription = form.data["subscription"]
        trainer = form.data["trainer"]
        courses = form.data["courses"]
        sub = Subscription.query.filter_by(name=subscription)[0]
        tr = Trainer.query.filter_by(name=trainer)[0]
        user = User(name=name, active=active, holder=sub, trainee=tr)
        for course in courses:
            for c in Course.query.all():
                if course == c.name:
                    user.courses.append(c)
        db.session.add(user)
        db.session.commit()
        if search_form.data["name"] != '':
            return search()
        else:
            pass

        return redirect(url_for("users_all", num=num))

    return render_template("members.html", num=num, users=users, trainers=trainers, subscriptions=subscriptions,
                           error=error, form=form, users_num=users_num, new_id=new_id, route=route, navs=navs, search_form=search_form)


@app.route('/add-edit-user/<int:user_id>', methods=["POST", "GET"])
@login_required
def user_details(user_id):
    search_form = SearchForm()
    route = "/users/0"
    new_id = user_id
    users_num = math.floor((len(User.query.all())) / 4)
    time = datetime.utcnow()
    if user_id == max([user.id for user in User.query.all()]) + 1:
        form = UserForm()
        if request.method == "POST":
            name = form.data["name"]
            active = form.data["active"]
            if form.data["subscription"] != '':
                holder = Subscription.query.filter_by(name=form.data["subscription"])[0]
            else:
                holder = None
            if form.data["trainer"] != '':
                trainee = Trainer.query.filter_by(name=form.data["trainer"])[0]
            else:
                trainee = None
            courses = []
            for course in form.data["courses"]:
                c = Course.query.filter_by(name=course)[0]
                courses.append(c)
            u = User(name=name, active=active, holder=holder, trainee=trainee, courses=courses)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for("users_all", num=users_num, search_form=search_form))

        return render_template("member.html", form=form, new_id=new_id, time=time, route=route, navs=navs, search_form=search_form)

    else:
        user = User.query.filter_by(id=user_id).first()
        data = {}
        if (user.holder is not None) and (user.trainee is not None):
            data = {'name': user.name, 'active': user.active, "subscription": user.holder.name, "trainer": user.trainee.name,
                    'courses': [course.name for course in user.courses]}
        elif (user.holder is not None) and (user.trainee is None):
            data = {'name': user.name, 'active': user.active, "subscription": user.holder.name,
                    "trainer": "",
                    'courses': [course.name for course in user.courses]}
        elif (user.holder is None) and (user.trainee is not None):
            data = {'name': user.name, 'active': user.active, "subscription": "",
                    "trainer": user.trainee,
                    'courses': [course.name for course in user.courses]}
        elif (user.holder is None) and (user.trainee is None):
            data = {'name': user.name, 'active': user.active, "subscription": "",
                    "trainer": "",
                    'courses': [course.name for course in user.courses]}
        form = UserForm(data=data)
        if request.method == "POST":
            user.name = form.data["name"]
            user.active = form.data["active"]
            if form.data["subscription"] != "":
                user.holder = Subscription.query.filter_by(name=form.data["subscription"])[0]
            else:
                user.holder = None
            if form.data["trainer"] != "":
                user.trainee = Trainer.query.filter_by(name=form.data["trainer"])[0]
            else:
                user.trainee = None
            user.courses = []
            if form.data["courses"] != ['']:
                for c in form.data["courses"]:
                    c = Course.query.filter_by(name=c)[0]
                    user.courses.append(c)
            db.session.commit()
            users = User.query.all()
            user_index = users.index(user)
            num = (len(User.query.all()[:user_index])) / 4
            return redirect(url_for("users_all", num=num))

        return render_template("member.html", user=user, form=form, new_id=new_id, navs=navs, route=route, search_form=search_form)


@app.route('/delete-user/<int:user_id>', methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("users_all", num=0))



@app.route('/trainers/<int:num>', methods=["GET", "POST"])
@login_required
def trainers_all(num):
    search_form = SearchForm()
    route = "/trainers/0"
    trainers = Trainer.query.all()[num * 4:num * 4 + 4]
    form = TrainerForm()
    trainers_num = math.ceil((len(Trainer.query.all())) / 4)
    new_id = max([trainer.id for trainer in Trainer.query.all()]) + 1

    return render_template("trainers.html", trainers=trainers, form=form, trainers_num=trainers_num, num=num,
                           new_id=new_id, route=route, navs=navs, search_form=search_form)


@app.route('/add-edit-trainer/<int:trainer_id>', methods=["POST", "GET"])
@login_required
def trainer_details(trainer_id):
    search_form = SearchForm()
    route = "/trainers/0"
    new_id = trainer_id
    if new_id == max([trainer.id for trainer in Trainer.query.all()]) + 1:
        form = TrainerForm()
        if request.method == "POST":
            name = form.data["name"]
            personal = form.data["personal"]
            classes = []
            if form.data["classes"] != ['']:
                for c in form.data["classes"]:
                    c = Course.query.filter_by(name=c)[0]
                    classes.append(c)
            t = Trainer(name=name, personal=personal, classes=classes)
            db.session.add(t)
            db.session.commit()
            trainers = Trainer.query.all()
            t_index = trainers.index(t)
            num = (len(trainers[:t_index])) // 4
            db.session.commit()
            return redirect(url_for("trainers_all", num=num))

        return render_template("trainer.html", form=form, new_id=new_id, num=0, navs=navs, route=route, search_form=search_form)
    else:
        trainer = Trainer.query.filter_by(id=trainer_id).first()
        data = {'name': trainer.name, 'personal': trainer.personal,
                'classes': [c.name for c in trainer.classes]}
        form = TrainerForm(data=data)
        if request.method == "POST":
            trainer.name = form.data["name"]
            trainer.personal = form.data["personal"]
            trainer.classes = []
            if form.data["classes"] != ['']:
                for c in form.data["classes"]:
                    c = Course.query.filter_by(name=c)[0]
                    trainer.classes.append(c)
            trainers = Trainer.query.all()
            trainer_index = trainers.index(trainer)
            num = (len(trainers[:trainer_index])) // 4
            db.session.commit()

            return redirect(url_for("trainers_all", num=num))

        return render_template("trainer.html", trainer=trainer, form=form, new_id=new_id, route=route, navs=navs, search_form=search_form)


@app.route('/delete-trainer/<int:trainer_id>', methods=["POST"])
@login_required
def delete_trainer(trainer_id):
    trainer = Trainer.query.filter_by(id=trainer_id).first_or_404()
    if trainer.trainees:
        users = User.query.filter_by(trainee=trainer)
        for user in users:
            user.trainee = None
    db.session.delete(trainer)
    db.session.commit()
    return redirect(url_for("trainers_all", num=0))



@app.route('/courses/<int:num>', methods=["GET", "POST"])
@login_required
def courses_all(num):
    search_form = SearchForm()
    route = "/courses/0"
    courses = Course.query.all()[num * 7:num * 7 + 7]
    courses_num = math.ceil((len(Course.query.all())) / 7)
    new_id = max([course.id for course in Course.query.all()])
    form = CourseForm()
    if request.method == "POST":
        name = form.data["name"]
        instructors = form.data["instructors"]
        course = Course(name=name)
        for instructor in instructors:
            for trainer in Trainer.query.all():
                if trainer.name == instructor:
                    course.instructors.append(trainer)
        db.session.add(course)
        db.session.commit()

        courses = Course.query.all()
        c_index = courses.index(course)
        num = (len(courses[:c_index])) // 7

        return redirect(url_for("courses_all", num=num))


    return render_template('courses.html', courses=courses, form=form, num=num, courses_num=courses_num, new_id=new_id,
                           search_form=search_form, route=route, navs=navs)

@app.route('/delete-course/<int:course_id>', methods=["POST"])
@login_required
def delete_course(course_id):
    course = Course.query.filter_by(id=course_id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for("courses_all", num=0))


@app.route('/subscriptions/<int:num>', methods=["GET", "POST"])
@login_required
def subscriptions_all(num):
    search_form = SearchForm()
    route = "/subscriptions/0"
    subscriptions = Subscription.query.all()[num * 7:num * 7 + 7]
    subs_num = math.ceil((len(Subscription.query.all())) / 7)
    form = SubscriptionForm()
    if request.method == "POST":
        name = form.data["name"]
        sub = Subscription(name=name)
        db.session.add(sub)
        db.session.commit()

        subs = Subscription.query.all()
        sub_index = subs.index(sub)
        num = (len(subs[:sub_index])) // 7

        return redirect(url_for("subscriptions_all", num=num))

    return render_template("subscriptions.html", subscriptions=subscriptions, form=form, num=num, subs_num=subs_num,
                           search_form=search_form, navs=navs, route=route)

@app.route('/delete-subscription/<int:sub_id>', methods=["POST"])
@login_required
def delete_subscription(sub_id):
    sub = Subscription.query.filter_by(id=sub_id).first_or_404()
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for("subscriptions_all", num=0))


