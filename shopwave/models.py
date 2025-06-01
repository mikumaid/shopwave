from shopwave import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # New field to indicate admin status

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    Images = db.Column(db.PickleType, nullable=False)  # Store images as a list
    description = db.Column(db.String(200), nullable=False)
    detail = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}', '{self.description}', '{self.detail}', '{self.Images}')"