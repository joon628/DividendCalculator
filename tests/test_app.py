import unittest
from flask_testing import TestCase
from unittest.mock import patch
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_dir, 'dividend_calculator'))
from app import app, db
from models import Stock
from dividend_calculator import DividendCalculator

class BaseTestCase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestStockRoutes(BaseTestCase):
    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_add_stock(self):
        with self.client:
            response = self.client.post('/add_stock', data=dict(ticker='SCHD', shares=10), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            stock = Stock.query.filter_by(ticker='SCHD').first()
            self.assertIsNotNone(stock)
            self.assertEqual(stock.shares, 10)

    def test_delete_stock(self):
        new_stock = Stock(ticker='SCHD', shares=10)
        db.session.add(new_stock)
        db.session.commit()

        response = self.client.get('/delete_stock/SCHD', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        stock = Stock.query.filter_by(ticker='SCHD').first()
        self.assertIsNone(stock)

    def test_edit_stock(self):
        new_stock = Stock(ticker='SCHD', shares=10)
        db.session.add(new_stock)
        db.session.commit()

        response = self.client.post('/edit_stock', data=dict(old_ticker='SCHD', new_ticker='SCHD', new_shares=20), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        stock = Stock.query.filter_by(ticker='SCHD').first()
        self.assertIsNotNone(stock)
        self.assertEqual(stock.shares, 20)

    def test_get_tickers(self):
        stock1 = Stock(ticker='SCHD', shares=10)
        stock2 = Stock(ticker='MSFT', shares=15)
        db.session.add_all([stock1, stock2])
        db.session.commit()

        response = self.client.get('/get_tickers')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('SCHD', data['tickers'])
        self.assertIn('MSFT', data['tickers'])

class TestDividendCalculator(unittest.TestCase):
    @patch('yfinance.Ticker')
    def test_get_quarterly_payout(self, mock_yfinance):
        mock_instance = mock_yfinance.return_value
        mock_instance.dividends.iloc.__getitem__.return_value = 2.0

        calculator = DividendCalculator('AAPL', 10)
        payout = calculator.get_quarterly_payout()
        self.assertEqual(payout, 20.0)

    @patch('yfinance.Ticker')
    def test_get_yearly_payout(self, mock_yfinance):
        mock_instance = mock_yfinance.return_value
        mock_instance.dividends.iloc.__getitem__.return_value = 2.0

        calculator = DividendCalculator('AAPL', 10)
        payout = calculator.get_yearly_payout()
        self.assertEqual(payout, 80.0)

if __name__ == '__main__':
    unittest.main()
