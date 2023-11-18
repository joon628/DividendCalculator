from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .extensions import db
from .dividend_calculator import DividendCalculator
from .models import Stock
import yfinance as yf

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    if  current_user.is_authenticated:
        stocks = Stock.query.filter_by(user_id=current_user.id).all()
    else:
        stocks = []
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


@routes.route('/add_stock', methods=['POST'])
@login_required
def add_stock():
    ticker = request.form['ticker']
    shares = float(request.form['shares'])

    existing_stock = Stock.query.filter_by(ticker=ticker, user_id=current_user.id).first()

    if existing_stock:
        existing_stock.shares += shares
    else:
        new_stock = Stock(ticker=ticker, shares=shares, user_id=current_user.id)
        db.session.add(new_stock)

    db.session.commit()
    return redirect(url_for('routes.index'))

@routes.route('/delete_stock/<string:ticker>', methods=['GET'])
@login_required
def delete_stock(ticker):
    Stock.query.filter_by(ticker=ticker, user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('routes.index'))

@routes.route('/edit_stock', methods=['POST'])
@login_required
def edit_stock():
    old_ticker = request.form['old_ticker']
    new_ticker = request.form['new_ticker']
    new_shares = request.form['new_shares']

    stock = Stock.query.filter_by(ticker=old_ticker, user_id=current_user.id).first()

    if stock:
        if new_ticker:
            stock.ticker = new_ticker
        if new_shares:
            stock.shares = float(new_shares)
        db.session.commit()

    return redirect(url_for('routes.index'))


@routes.route('/get_tickers')
@login_required
def get_tickers():
    tickers = [stock.ticker for stock in Stock.query.filter_by(user_id=current_user.id).with_entities(Stock.ticker).distinct()]
    return {'tickers': tickers}




