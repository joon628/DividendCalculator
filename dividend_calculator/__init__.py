from flask import Flask
from .extensions import db, login_manager
from .dividend_calculator import DividendCalculator
from .models import Stock, User
from .app import routes
from flask_login import login_user, LoginManager
from .auth import auth as auth_blueprint

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_very_long_random_secret_key'

    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        db.create_all()

    app.register_blueprint(routes)
    app.register_blueprint(auth_blueprint)
    login_manager.login_view = 'auth.login'
    
    
    return app