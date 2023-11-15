from flask import Flask, render_template, request, redirect, url_for
from extensions import db
import yfinance as yf
from dividend_calculator import DividendCalculator
from models import Stock

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    stocks = Stock.query.all()

    total_quarterly_payout = 0
    total_yearly_payout = 0
    stock_details = []

    for stock in stocks:
        ticker, shares = stock.ticker, stock.shares
        calculator = DividendCalculator(ticker, shares)
        quarterly_payout = calculator.get_quarterly_payout()
        yearly_payout = calculator.get_yearly_payout()

        total_quarterly_payout += quarterly_payout
        total_yearly_payout += yearly_payout

        stock_details.append((ticker, shares, round(quarterly_payout, 4), round(yearly_payout, 4)))

    return render_template('index.html', stocks=stock_details, 
                           total_quarterly=round(total_quarterly_payout, 2), 
                           total_yearly=round(total_yearly_payout, 2))


@app.route('/add_stock', methods=['POST'])
def add_stock():
    ticker = request.form['ticker']
    shares = float(request.form['shares'])

    existing_stock = Stock.query.filter_by(ticker=ticker).first()

    if existing_stock:
        existing_stock.shares += shares
    else:
        new_stock = Stock(ticker=ticker, shares=shares)
        db.session.add(new_stock)

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_stock/<string:ticker>', methods=['GET'])
def delete_stock(ticker):
    Stock.query.filter_by(ticker=ticker).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit_stock', methods=['POST'])
def edit_stock():
    old_ticker = request.form['old_ticker']
    new_ticker = request.form['new_ticker']
    new_shares = request.form['new_shares']

    stock = Stock.query.filter_by(ticker=old_ticker).first()

    if stock:
        if new_ticker:
            stock.ticker = new_ticker
        if new_shares:
            stock.shares = float(new_shares)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/get_tickers')
def get_tickers():
    tickers = [stock.ticker for stock in Stock.query.with_entities(Stock.ticker).distinct()]
    return {'tickers': tickers}



if __name__ == '__main__':
    app.run(debug=True)
