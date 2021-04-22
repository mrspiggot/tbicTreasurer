import sqlalchemy
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from forex_python.converter import CurrencyRates
from pathlib import Path
import plotly.express as px
from datetime import date, timedelta
import yahoo_fin.stock_info as si
import dash_table
from babel.numbers import format_currency
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
rates.update({'GBP': 100})
cwd = Path.cwd()






def get_portfolio_data():

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
    df_last_meeting = pd.read_sql('SELECT * FROM tbic_stock_meeting where meeting_num in (select max(meeting_num) from tbic_stock_meeting)', engine)
    df_lm = df_last_meeting.merge(tbic_df, on='ticker')
    df_tm = df_real_time.merge(df_lm, on='ticker')
#    df_tm['new_gbp'] = format_currency(df_tm['gbp_pos'] * df_tm['Qty'], 'GBP', locale='en_US')
#    df_tm['delta'] = format_currency(df_tm['new_gbp'] - df_tm['gbp_position'], 'GBP', locale='en_US')

    df_tm['new_gbp'] = df_tm['gbp_pos'] * df_tm['Qty']
    df_tm['delta'] = df_tm['new_gbp'] - df_tm['gbp_position']
    df_tm['pct_gain'] = df_tm['delta']/df_tm['gbp_position']
    df_tm = df_tm[['ticker', 'name', 'currency_x', 'Qty', 'quote_x', 'new_gbp', 'delta', 'pct_gain', 'sector', 'industry', 'owner']]
    df_tm.columns = ['Ticker', 'Company Name', 'CCY', 'Qty', 'Quote', 'GBP Value', 'GBP Gain', '% Gain', 'Sector', 'Industry', 'Owner']
#    df_tm['quote_x'] = pd.to_numeric(df_tm['quote_x'], errors='coerce')
#    df_tm['quote_x'] = df_tm['quote_x'].map('{:,.0f}'.format)
#    df_tm['Value'] = df_tm['GBP Value']
#    df_tm['Gain'] = df_tm['% Gain']
#    df_tm['GBP Value'] = df_tm['GBP Value'].map('{:,.2f}'.format)
#    df_tm['GBP Gain'] = df_tm['GBP Gain'].map('{:,.2f}'.format)
    df_tm['% Gain'] = df_tm['% Gain']*100
#    df_tm['% Gain'] = df_tm['% Gain'].map('{:,.2f}'.format)
#    df_tm['GBP Value'] = pd.to_numeric(df_tm['GBP Value'], errors='coerce')


    return df_tm
'''
def format_table():
    tbic_port = get_portfolio_data()
    print(tbic_port.info())
    display_port = tbic_port[['ticker', 'name', 'currency_x', 'quote_x', 'new_gbp', 'delta', 'pct_gain', 'sector', 'industry', 'owner']]
    display_port.sort_values(by='delta', ascending=False, inplace=True)
    display_port['quote_x'] = display_port['quote_x'].map('{:,.0f}'.format)
    display_port['new_gbp'] = display_port['new_gbp'].map('{:,.0f}'.format)
    display_port['delta'] = display_port['delta'].map('{:,.0f}'.format)
    display_port['pct_gain'] = display_port['pct_gain']*100
    display_port['pct_gain'] = display_port['pct_gain'].map('{:,.0f}'.format)
    display_port.columns = [['Ticker', 'Name', 'CCY', 'Quote (in CCY)', 'GBP Value', 'GBP Gain (Loss)', 'GBP % Gain (Loss)', 'Sector', 'Industry', 'Owner']]

    return display_port
'''
def portfolio_table():
    '''
    tbic_port = get_portfolio_data()
    print(tbic_port.info())
    display_port = tbic_port[['Ticker', 'Company Name', 'CCY', 'Qty', 'Quote', 'GBP Value', 'GBP Gain', '% Gain', 'Sector', 'Industry', 'Owner']]
    display_port.sort_values(by='GBP Value', ascending=False, inplace=True)
#    display_port['quote_x'] = display_port['quote_x'].map('{:,.0f}'.format)
    display_port['GBP Value'] = display_port['GBP Value'].map('{:,.0f}'.format)
    display_port['GBP Gain'] = display_port['GBP Gain'].map('{:,.0f}'.format)
    display_port['% Gain'] = display_port['% Gain']*100
    display_port['% Gain'] = display_port['% Gain'].map('{:,.0f}'.format)
    display_port.columns = [['Ticker', 'Name', 'CCY', 'Qty', 'Quote', 'GBP_Value', 'GBP_Gain', 'GBP_% Gain', 'Sector', 'Industry', 'Owner']]
'''
    df = get_portfolio_data()
    df['GBP Value'] = pd.to_numeric(df['GBP Value'], errors='coerce')
    df['GBP Gain'] = pd.to_numeric(df['GBP Gain'], errors='coerce')
    df['% Gain'] = pd.to_numeric(df['% Gain'], errors='coerce')
    df.round({'GBP Value': 2, 'GBP Gain': 2, '% Gain': 2})
    df['GBP Value'] = df['GBP Value'].round(decimals=2)
    df['GBP Gain'] = df['GBP Gain'].round(decimals=2)
    df['% Gain'] = df['% Gain'].round(decimals=2)
    df.sort_values(by='GBP Gain', ascending=False, inplace=True)
 #   return dbc.Table.from_dataframe(display_port, striped=True, bordered=True, hover=True)
    return dash_table.DataTable(id='tbic_table',
                                columns=[{"name": i, "id": i} for i in df.columns],
                                data=df.to_dict('records'),  # the contents of the table
        editable=True,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=True,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="native",       # all data is passed to the table up-front or not ('none')
        page_current=0,             # page number that user is on
        page_size=32,                # number of rows visible per page
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'width': '{}%'.format(len(df.columns)),
            'textOverflow': 'ellipsis',
            'overflow': 'hidden'
        },
        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'right',
                'width': '60px',
            } for c in ['Ticker', 'CCY', 'Qty', 'Owner', 'Quote', 'GBP Value', 'GBP Gain', '% Gain']

        ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    )

def portfolio_treemap():
    tbic_port = get_portfolio_data()
    tbic_port["portfolio"] = "The TBIC Portfolio - Go Bears!! (Click to drill down...)"
#    tbic_port.to_pickle(cwd.joinpath("assets/sector_tree.pkl"))

    fig = px.treemap(tbic_port, path=['portfolio', 'Sector', 'Industry', 'Company Name'],
                     values='GBP Value', color='% Gain', color_continuous_scale='thermal')

    return dcc.Graph(figure=fig)

layout = html.Div([
    html.H1('TBIC Portfolio - Performance since last meeting', style={'textAlign': 'center'}),

        portfolio_treemap(),
        portfolio_table(),

])