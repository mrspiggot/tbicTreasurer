from pathlib import Path
from app import app
from app import server
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import sqlalchemy
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
from apps import portfolio, currency, owner, stype, sector, research, semple_slicer, bubble, region, country

cwd = Path.cwd()


img = Image.open(cwd.joinpath('tbicTreasurer/assets/Clear Bear.png'))

covid_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Oxford Bubble Chart", href='/bubble'),
        dbc.DropdownMenuItem("Oxford Index", href='https://player.vimeo.com/video/463163595'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Country Comparison", href='/ox_country'),
        dbc.DropdownMenuItem("Region Comparison", href='/ox_region'),
        ],
    nav=True,
    in_navbar=True,
    label="C-19",
)
research_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Undervalued Large Caps", href='/uv_large_cap'),
        dbc.DropdownMenuItem("Most Shorted Stocks", href='/most_shorted', disabled=True),
        dbc.DropdownMenuItem("Aggressive Small Caps", href='/ag_small_cap', disabled=True),
        dbc.DropdownMenuItem("Undervalued Growth Stocks", href='/uv_growth_stock', disabled=True),
        ],
    nav=True,
    in_navbar=True,
    label="Research",
)
heatmap_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Sector", href='/sector'),
        dbc.DropdownMenuItem("Stock Type", href='/stype'),
        dbc.DropdownMenuItem("Currency", href='/currency'),
        dbc.DropdownMenuItem("Owner", href='/owner'),
        ],
    nav=True,
    in_navbar=True,
    label="Heatmaps",
)
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=img, height="90px")),
                        dbc.Col(dbc.NavbarBrand("TBIC Portfolio", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    [dbc.NavItem(dbc.NavLink("Intra-Month Performance", href="/performance", disabled=True)),
                     dbc.NavItem(dbc.NavLink("Semple's Scimitar", href="/semple")),
                     heatmap_dropdown,
                     research_dropdown,
                     covid_dropdown,
                     ], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),

        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
app.layout = html.Div([
    dcc.Location(id='page-url'),
    html.Div([
        navbar,
    ]),
    html.Div(id='page-content', children=[]),
],
style=CONTENT_STYLE)

@app.callback(Output('page-content', 'children'),
              [Input('page-url', 'pathname')], prevent_initial_call=True)
def display_page(pathname):
    if pathname == '':
        return portfolio.layout
    if pathname == '/sector':
        return sector.layout
    if pathname == '/stype':
        return stype.layout
    if pathname == '/currency':
        return currency.layout
    if pathname == '/owner':
        return owner.layout
    if pathname == '/uv_large_cap':
        return research.layout
    if pathname == '/semple':
        return semple_slicer.layout
    if pathname == '/bubble':
        return bubble.layout
    if pathname == '/ox_country':
        return country.layout
    if pathname == '/ox_region':
        return region.layout
    else:
        return portfolio.layout

if __name__ == '__main__':
    app.run_server(debug=True)