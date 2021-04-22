from forex_python.converter import CurrencyRates
from pathlib import Path
import pandas as pd
import sqlalchemy
import yahoo_fin.stock_info as si
from datetime import timedelta
from decouple import config
NAME = config('DB_NAME')
USER = config('DB_USER')
PASSWORD = config('DB_PASSWORD')
HOST = config('DB_HOST')
PORT = config('DB_PORT')
engine = sqlalchemy.create_engine('postgresql://' + str(USER) + ":" + str(PASSWORD) + "@" + str(HOST) + ":" + str(PORT) + "/" + str(NAME))

c = CurrencyRates()
rates = c.get_rates('GBP')
rates.update({'GBP': 100})
cwd = Path.cwd()


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.currency = self.get_currency()
        self.yahoo_ticker = self.xref()

    def get_currency(self):
        query = "select currency from tbic_stocks where ticker = '" + str(self.ticker) + "'"
        ccy = pd.read_sql(query, engine)['currency'].to_list()[0]
        return ccy

    def xref(self):
        query = "select code from cross_reference where ticker = '" + str(self.ticker) + "' and system = 'Yahoo'"
        yahoo_ticker = pd.read_sql(query, engine)['code'].to_list()[0]
        return yahoo_ticker

    def get_quote(self, quote_date):
        try:
            quote = si.get_data(self.yahoo_ticker, start_date=quote_date, end_date=quote_date + timedelta(days=1))
        except:
            prev_date = quote_date - timedelta(days=1)
            quote = si.get_data(self.yahoo_ticker, start_date=prev_date, end_date=prev_date + timedelta(days=1))

        return quote

    def get_quote_in_gbp(self, quote_date):
        gbp = rates[self.currency]
        try:
            quote = si.get_data(self.yahoo_ticker, start_date=quote_date, end_date=quote_date + timedelta(days=1))
        except:
            prev_date = quote_date - timedelta(days=1)
            quote = si.get_data(self.yahoo_ticker, start_date=prev_date, end_date=prev_date + timedelta(days=1))

        quote[['open', 'high', 'low', 'close', 'adjclose']] = quote[['open', 'high', 'low', 'close', 'adjclose']] / gbp
        return quote

    def get_live_price(self):
        quote = si.get_live_price(self.yahoo_ticker)
        if self.currency == 'GBP':
            quote = quote / 100

        quote = format_currency(quote, self.currency, locale='en_US')
        return quote

    def get_live_price_in_gbp(self):
        gbp = rates[self.currency]
        quote = si.get_live_price(self.yahoo_ticker) / gbp
        return quote

    def get_data(self, start_date, end_date):
        quote = si.get_data(self.yahoo_ticker, start_date, end_date)
        return quote

    def get_latest_from_db(self, date):
        try:
            quote = pd.read_sql("select * from stock_quote where ticker = '" + str(self.yahoo_ticker) + "' and index = '" + str(date) + "'", engine)['adjclose'].to_list()[0]
        except:
            last_date = pd.read_sql("select max(index) from stock_quote where ticker = '" + str(self.yahoo_ticker) + "'", engine)['max'].to_list()[0]

            quote = pd.read_sql(
                "select * from stock_quote where ticker = '" + str(self.yahoo_ticker) + "' and index = '" + str(last_date) + "'",
                engine)['adjclose'].to_list()[0]
        return quote

    def get_latest_from_db_in_gbp(self, date):
        gbp = rates[self.currency]
        try:
            quote = pd.read_sql("select * from stock_quote where ticker = '" + str(self.yahoo_ticker) + "' and index = '" + str(date) + "'", engine)['adjclose'].to_list()[0]
        except:
            last_date = pd.read_sql("select max(index) from stock_quote where ticker = '" + str(self.yahoo_ticker) + "'", engine)['max'].to_list()[0]

            quote = pd.read_sql(
                "select * from stock_quote where ticker = '" + str(self.yahoo_ticker) + "' and index = '" + str(last_date) + "'",
                engine)['adjclose'].to_list()[0]
        return quote / gbp