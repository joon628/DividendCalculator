from flask import Flask
from .extensions import db
from .dividend_calculator import DividendCalculator
from .models import Stock
from .app import routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .app import routes
    app.register_blueprint(routes)

    return app
