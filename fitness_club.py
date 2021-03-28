from app import app, db
from app.models import User, Subscription, Trainer, Course, association_table, association_table_2

@app.shell_context_processor
def make_shell_context():
   return {
       "db": db,
       "User": User,
       "Subscription": Subscription,
       "Trainer": Trainer,
       "Course": Course,
       "association_table": association_table,
       "association_table_2": association_table_2
   }

if __name__ == "__main__":
    app.run(debug=True)