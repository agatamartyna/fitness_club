from app import db
from datetime import datetime

association_table = db.Table('association_table', db.Model.metadata,
                             db.Column(
                                 'user_id',
                                 db.Integer,
                                 db.ForeignKey('user.id')
                             ),
                             db.Column(
                                 'course_id',
                                 db.Integer,
                                 db.ForeignKey('course.id')
                             ))

association_table_2 = db.Table('association_table_2', db.Model.metadata,
                               db.Column(
                                   'trainer_id',
                                   db.Integer,
                                   db.ForeignKey('trainer.id')
                               ),
                               db.Column(
                                   'course_id',
                                   db.Integer,
                                   db.ForeignKey('course.id')
                               ))


class Subscription(db.Model):
    __tablename__ = "subscription"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    users = db.relationship("User", backref="holder", lazy="dynamic")

    def __str__(self):
        return "subscription"


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    sign_up = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))
    courses = db.relationship("Course",
                              secondary=association_table,
                              back_populates="users",
                              lazy="subquery"
                              )

    def __str__(self):
        return "user"


class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    personal = db.Column(db.Boolean, default=False)
    trainees = db.relationship("User", backref="trainee", lazy="dynamic")
    classes = db.relationship("Course",
                              secondary=association_table_2,
                              back_populates="instructors",
                              lazy="subquery")

    def __str__(self):
        return "trainer"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    instructors = db.relationship("Trainer",
                                  secondary=association_table_2,
                                  back_populates="classes",
                                  lazy="subquery")
    users = db.relationship("User",
                            secondary=association_table,
                            back_populates="courses",
                            lazy="subquery")

    def __str__(self):
        return "course"
