from app.models import User, Trainer, Subscription, Course
from app.forms import SearchForm
from flask import request, redirect, url_for
import math

navs = [("Uczestnicy", "/users/0"), ("Trenerzy", "/trainers/0"), ("Zajęcia", "/courses/0"), ("Abonamenty", "/subscriptions/0")]


def search():
    search_form = SearchForm()
    if request.method == "POST":
        name = (search_form.data["name"]).lower()
        objects = [User, Trainer, Subscription, Course]
        names = []
        for object in objects:
            for item in object.query.all():
                names.append((item.name, item.id, str(item)))
        result = []
        for nam in names:
            if nam[0].lower() == name:
                result.append(nam)
        if result:
            if result[0][2] == 'user':
                return redirect(url_for("user_details", user_id=result[0][1]))
            elif result[0][2] == "trainer":
                return redirect(url_for("trainer_details", trainer_id=result[0][1]))
            elif result[0][2] == "subscription":
                subs = Subscription.query.all()
                subss = [(sub.id, sub.name, subs.index(sub)) for sub in subs]
                num = 0
                for s in subss:
                    if s[1] == result[0][0]:
                        num = math.floor(s[2] / 7)
                return redirect(url_for("subscriptions_all", num=num))
            elif result[0][2] == "course":
                courses = Course.query.all()
                coursess = [(course.id, course.name, courses.index(course)) for course in courses]
                num = 0
                for c in coursess:
                    if c[1] == result[0][0]:
                        num = math.floor(c[2] / 7)
                return redirect(url_for("courses_all", num=num))

