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
slider_dict = {1: '1m', 2: "2m", 3: '3m', 4: '6m', 5: '1Y', 6: '2Y'}
meeting_list = [0,0,1,2,5,11,23]






def get_portfolio_data(val):

    tbic_df = pd.read_sql_table('tbic_stocks', engine)
    tickers = tbic_df['ticker'].to_list()

    position = []
    for ticker in tickers:
        stock = Stock(ticker)
        price = stock.get_latest_from_db(date.today())
        value = stock.get_latest_from_db_in_gbp(date.today())
        d = {
            'ticker': ticker,
            'quote': price,
            'gbp_pos': value
        }
        position.append(d)
    df_real_time = pd.DataFrame(position)
    last_meeting = pd.read_sql('SELECT meeting_num FROM tbic_stock_meeting where meeting_num in (select max(meeting_num) from tbic_stock_meeting)', engine)['meeting_num'].to_list()[0]

    meeting_num = last_meeting-meeting_list[int(val)]

    df_last_meeting = pd.read_sql("SELECT * FROM tbic_stock_meeting where meeting_num = '" + str(meeting_num) + "'", engine)
    df_lm = df_last_meeting.merge(tbic_df, on='ticker')
    df_tm = df_real_time.merge(df_lm, on='ticker')


    df_tm['new_gbp'] = df_tm['gbp_pos'] * df_tm['Qty']
    df_tm['delta'] = df_tm['new_gbp'] - df_tm['gbp_position']
    df_tm['pct_gain'] = df_tm['delta']/df_tm['gbp_position']
    df_tm = df_tm[['ticker', 'name', 'currency_x', 'Qty', 'quote_x', 'new_gbp', 'delta', 'pct_gain', 'sector', 'industry', 'owner']]
    df_tm.columns = ['Ticker', 'Company Name', 'CCY', 'Qty', 'Quote', 'GBP Value', 'GBP Gain', '% Gain', 'Sector', 'Industry', 'Owner']

    df_tm['% Gain'] = df_tm['% Gain']*100

    return df_tm




layout = html.Div([
    html.H1('TBIC Shares by Stock Owner', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(
            dcc.Slider(min=1, max=6, marks=slider_dict, id="owner-treemap-slider", value=1),
            width=7, lg={'size': 6,  "offset": 0, 'order': 'first'}
        ),
        dbc.Col(html.H5('Move Slider to see gains (losses) over different timeframes'),
            width=4, lg={'size': 6,  "offset": 0, 'order': 'first'}),
    ]),
    dbc.Spinner(dcc.Graph(id='owner-treemap', figure = {}), color='primary'),
])
@app.callback(Output('owner-treemap', 'figure'),
              [Input('owner-treemap-slider', 'value')])
def currency_treemap(value):
    tbic_port = get_portfolio_data(value)

    tbic_port["portfolio"] = "The TBIC Portfolio - By Stock Owner"
    fig = px.treemap(tbic_port, path=['portfolio', 'Owner', 'CCY', 'Sector', 'Industry', 'Company Name'],
                     values='GBP Value', color='% Gain', color_continuous_scale='thermal',
                     height=700)

    return fig