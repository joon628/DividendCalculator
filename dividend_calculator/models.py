from .extensions import db
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String, nullable=False)
    shares = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Stock {self.ticker}>"