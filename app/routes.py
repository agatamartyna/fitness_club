from flask import render_template, request, redirect, url_for
from app.models import User, Subscription, Trainer, Course
from app import app, db
from app.forms import UserForm, CourseForm, TrainerForm, SubscriptionForm

@app.route('/users', methods=["GET", "POST"])
def users_all():
    users = User.query.all()
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

        return redirect(url_for("users_all"))

    return render_template("users.html", users=users, trainers=trainers, subscriptions=subscriptions, error=error, form=form)


@app.route('/users/<int:user_id>', methods=["POST", "GET"])
def user_details(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    data = {'name':user.name, 'active':user.active,
            'subscription':user.holder.name,
            'trainer':user.trainee.name,
            'courses':[course.name for course in user.courses]}
    form = UserForm(data=data)
    if request.method == "POST":
        user.name = form.data["name"]
        user.active = form.data["active"]
        user.holder = Subscription.query.filter_by(name=form.data["subscription"])[0]
        user.trainee = Trainer.query.filter_by(name=form.data["trainer"])[0]
        user.courses = []
        for course in form.data["courses"]:
            c = Course.query.filter_by(name=course)[0]
            user.courses.append(c)
        db.session.commit()

        return redirect(url_for("users_all"))

    return render_template("user.html", user=user, form=form)

@app.route('/delete-user/<int:user_id>', methods=["POST"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("users_all"))


@app.route('/courses', methods=["GET", "POST"])
def courses_all():
    courses = Course.query.all()
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

        return redirect(url_for("courses_all"))

    return render_template('courses.html', courses=courses, form=form)


@app.route('/trainers', methods=["GET", "POST"])
def trainers_all():
    trainers = Trainer.query.all()
    form = TrainerForm()

    if request.method == "POST":
        name = form.data["name"]
        personal = form.data["personal"]
        classes = form.data["classes"]
        trainer = Trainer(name=name, personal=personal)
        db.session.add(trainer)
        for c in classes:
            for course in Course.query.all():
                if c == course.name:
                    trainer.classes.append(course)
        db.session.commit()

        return redirect(url_for("trainers_all"))

    return render_template("trainers.html", trainers=trainers, form=form)

@app.route('/trainers/<int:trainer_id>', methods=["GET", "POST"])
def trainer_details(trainer_id):
    trainer = Trainer.query.filter_by(id=trainer_id).first_or_404()
    data = {"name": trainer.name, "personal": trainer.personal, "classes": [course.name for course in trainer.classes]}
    form = TrainerForm(data=data)
    if request.method == "POST":
        trainer.name = form.data["name"]
        trainer.personal = form.data["personal"]
        trainer.classes = []
        for course in form.data["classes"]:
            c = Course.query.filter_by(name=course)[0]
            trainer.classes.append(c)
        db.session.commit()

        return redirect(url_for("trainers_all"))

    return render_template("trainer.html", trainer=trainer, form=form)


@app.route('/delete-trainer/<int:trainer_id>', methods=["POST"])
def delete_trainer(trainer_id):
    trainer = Trainer.query.filter_by(id=trainer_id).first_or_404()
    db.session.delete(trainer)
    db.session.commit()
    return redirect(url_for("trainers_all"))


@app.route('/subscriptions', methods=["GET", "POST"])
def subscriptions_all():
    subscriptions = Subscription.query.all()
    form = SubscriptionForm()
    if request.method == "POST":
        name = form.data["name"]
        sub = Subscription(name=name)
        db.session.add(sub)
        db.session.commit()

        return redirect(url_for("subscriptions_all"))

    return render_template("subscriptions.html", subscriptions=subscriptions, form=form)






