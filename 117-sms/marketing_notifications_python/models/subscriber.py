from marketing_notifications_python.models import app_db

db = app_db()


class Subscriber(db.Model):
    __tablename__ = "subscribers"

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String, nullable=False)
    subscribed = db.Column(db.Boolean, nullable=False, default=False)  # changed default to False
    # adding Comadre's fields below and to __repr__
    spanish = db.Column(db.Boolean, nullable=True, default=False)
    zipcode = db.Column(db.Integer, nullable=True)
    age = db.Column(db.String, nullable=True)
    interests = db.Column(db.String, nullable=True)


    def __repr__(self):
        return '<Subscriber %r %r %r %r %r>' % self.phone_number, self.subscribed, self.zipcode, self.age, self.interests
