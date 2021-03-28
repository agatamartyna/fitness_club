from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired
from app.models import Trainer, Subscription, Course


class UserForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    active = BooleanField("active", default=True)
    trainer = SelectField("Trainer")
    subscription = SelectField("Subscription")
    courses = SelectMultipleField("Course")


    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.trainer.choices = [''] + [trainer.name for trainer in Trainer.query.filter_by(personal=True).all()]
        self.subscription.choices = [''] + [subscription.name for subscription in Subscription.query.all()]
        self.courses.choices = [('', '')] + [(course.name, course.name) for course in Course.query.all()]




class CourseForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    instructors = SelectMultipleField("instructors")

    def __init__(self):
        super(CourseForm, self).__init__()
        self.instructors.choices = [('', '')] + [(trainer.name, trainer.name) for trainer in Trainer.query.all()]


class TrainerForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    personal = BooleanField("personal")
    classes = SelectMultipleField("classes")

    def __init__(self, *args, **kwargs):
        super(TrainerForm, self).__init__(*args, **kwargs)
        self.classes.choices = [(course.name, course.name) for course in Course.query.all()]

class SubscriptionForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
