import sqlalchemy
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app
from forex_python.converter import CurrencyRates
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from .portfolio import Stock
from dash.dependencies import Input, Output, State
from apps.helpers import Stock
from decouple import config
NAME = config('DB_NAME')
USER = config('DB_USER')
PASSWORD = config('DB_PASSWORD')
HOST = config('DB_HOST')
PORT = config('DB_PORT')
engine = sqlalchemy.create_engine('postgresql://' + str(USER) + ":" + str(PASSWORD) + "@" + str(HOST) + ":" + str(PORT) + "/" + str(NAME))

c = CurrencyRates()
rates = c.get_rates('GBP')
rates.update({'GBp': 100.0})
cwd = Path.cwd()
slider_dict = {1: '1m', 2: "2m", 3: '3m', 4: '4m', 5: '5m', 6: '6m'}
meeting_list = [0,1,2,3,4,5]


def order(A):
    if len(A) != len(set(A)):
        return 'Neither'
    elif A == sorted(A,reverse=False):
        return 'Ascending'
    elif A == sorted(A,reverse=True):
        return 'Descending'
    else:
        return 'Neither'

layout = html.Div([
    html.H4('Shares in decline - These shares are below their value at the last meeting, and have declined at each of the previous "n" meetings', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(
            dcc.Slider(min=1, max=6, marks=slider_dict, id="semple-slider", value=3),
            width=9, lg={'size': 6,  "offset": 0, 'order': 'first'}
        ),
        dbc.Col(html.H6('Move Slider to extend the lookback window (i.e. extend "n")'),
            width=3, lg={'size': 6,  "offset": 0, 'order': 'first'}),
    ]),
    dbc.Spinner(
        dbc.Row([
            dbc.Col(width=1, lg={'size': 1, "offset": 0, 'order': 'first'}),
            dbc.Col(html.Div(id='page-semple', children=[]), width=9, lg={'size': 9,  "offset": 2, 'order': 'first'}),

        ])
    )
])
@app.callback(Output('page-semple', 'children'),
              [Input('semple-slider', 'value')])
def semple_table(svalue):
    tbic = pd.read_sql_table('tbic_stocks', engine)
    ticker_list = tbic['ticker'].to_list()

    last_meeting = pd.read_sql(
        'SELECT meeting_num FROM tbic_stock_meeting where meeting_num in (select max(meeting_num) from tbic_stock_meeting)',
        engine)['meeting_num'].to_list()[0]

    meeting_num = last_meeting - svalue

    df_last_meeting = pd.read_sql(
        "SELECT ticker, meeting_num, quote FROM tbic_stock_meeting where meeting_num > '" + str(meeting_num) + "'",
        engine)
    df_lm = df_last_meeting.merge(tbic, on='ticker')

    position = []
    for ticker in ticker_list:
        stock = Stock(ticker)
        num = last_meeting + 1
        value = stock.get_latest_from_db(date.today())
        d = {
            'ticker': ticker,
            'meeting_num': num,
            'quote': value
        }
        position.append(d)
    df_real_time = pd.DataFrame(position)

    result = pd.concat([df_real_time, df_last_meeting])
    # print("Result = ", result.info())
    result.to_excel('Result.xlsx')
    result.sort_values(['meeting_num'], ascending=True, inplace=True)
    dogs = []
    for ticker in ticker_list:
        df = result[result['ticker'] == ticker]
        df_o = df[['ticker', 'meeting_num', 'quote']]
        df_l = df_o['quote'].to_list()
        #print(df_o)
        #print(df_l)
        #print("Ticker: ", ticker, "Order: ", order(df_l))
        if order(df_l) == 'Descending':
            dogs.append(ticker)
    today = date.today()
    six_m = today - timedelta(days=svalue*30)
    layout_rows = []
    for ticker in dogs:
        stock = Stock(ticker)
        sql_string = "select * from stock_quote where ticker = '" + str(stock.yahoo_ticker) + "' and index > '" + str(six_m) + "'"
        df = pd.read_sql(sql_string, engine)

        chart = go.Figure(data=go.Candlestick(x=df['index'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close']),
                        )
        chart.update_layout(title=str(ticker) + " share price", yaxis_title=stock.currency, xaxis_title="Date")
        candle = dcc.Graph(figure=chart)

        name = pd.read_sql("Select name from tbic_stocks where ticker = '" + str(ticker) + "'", engine)['name'].to_list()[0]
        row = dbc.Row([

            dbc.Card(
                candle)])
        layout_rows.append(row)

    return layout_rows