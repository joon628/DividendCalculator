import yfinance as yf

class DividendCalculator:
    def __init__(self, ticker, num_stocks):
        self.ticker = ticker
        self.num_stocks = num_stocks

    def get_quarterly_payout(self):
        stock = yf.Ticker(self.ticker)
        dividend = stock.dividends.iloc[-1]  
        payout = dividend * self.num_stocks
        return payout

    def get_yearly_payout(self):
        stock = yf.Ticker(self.ticker)
        dividend = stock.dividends.iloc[-1] 
        payout = dividend * self.num_stocks * 4  
        return payout