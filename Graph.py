import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output,Event,Input
import plotly
import pyodbc
import pandas as pd
import plotly.graph_objs as go
from collections import deque
from datetime import datetime


#Database Access
cnxn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server}'
                          ';Server=tcp:year4bitcoin.database.windows.net,1433;'
                          'Database=year4Proj;Uid=mikey96g@year4bitcoin;Pwd={Tallaght123!};'
                          'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
cursor = cnxn.cursor()

X = deque(maxlen=20)
X.append(1)
Y = deque(maxlen=20)
Y.append(1)

app_colors = {
    'background': '#000000',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}
def return_prediction():
    sql = "Select TOP 1 lstmSent from dbo.results Order BY  rDate  ,rTime   DESC "
    sq = pd.read_sql(sql, cnxn)
    sq = sq.values
    return sq[0]

def return_prediction2():
    sql = "Select TOP 1 lstmMulti from dbo.results Order BY  rDate  ,rTime   DESC "
    sq = pd.read_sql(sql, cnxn)
    sq = sq.values
    return sq[0]



app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(
    [

    html.Div(className='container-fluid', children=[html.H2('Live Bitcoin Predictions', style={'color': "#ffffff"})]),
    html.Hr(),
    html.Div(className='row', children=[
        html.Div(dcc.Graph(id='live-graph', animate=False),className='col s12 m8 l6'),html.Div(dcc.Graph(id='versus-graph', animate=False), className='col s12 m4 l6')]),
    html.Div(className='row',children=
    [
        html.Div(dcc.Graph(id='price-graph', animate=False), className='col s12 m8 l6'),
        html.Div (children=
        [
                (html.Button('Click for LSTM', id='button')),

        ]),

        html.H5(id='button-clicks',style={'color': "#ffffff"}),
        html.Div(children=
        [
            (html.Button('Click for Multi', id='button2'))
        ]),
        html.H5(id='multi',style={'color': "#ffffff"}),

        html.Div(children=
        [
            html.A(html.Button('View Sentiment Process', id='button2'), href='https://drive.google.com/open?id=1uD-J-micQiuupcPchWCiOOdt09AD0-sk',target="_blank"),
        ]),
    ]),



    html.Hr(),





        dcc.Interval(
            id='graph-update',
            interval=60000,
        ),

    ],style={'backgroundColor': app_colors['background']},
)


@app.callback(Output('live-graph', 'figure'),
              events=[Event('graph-update', 'interval')])

def update_graph_scatter():

    sql = "Select * from dbo.SentimentValues Order BY  dateS ,timeS  DESC"
    df = pd.read_sql(sql, cnxn)

    X = df.timeS.values[-20:]
    Y = df.sentVal.values[-20:]
    Y2 = df.sentTotal.values

    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Sentiment',
            mode= 'lines',
            yaxis= 'y2',
            line = dict(color=(app_colors['sentiment-plot']),
            width=4, )
            )

    data2 = plotly.graph_objs.Bar(
        x=X,
        y=Y2,
        name='Volume',
        marker=dict(color=app_colors['volume-bar']),

    )
    return {'data': [data,data2],'layout': go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y2),max(Y2*3)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)}


@app.callback(Output('versus-graph', 'figure'),
              events=[Event('graph-update', 'interval')])

def update_versus_graph():
    sql = "Select * from dbo.BitcoinVal Order BY dateB ,dboTime "
    df = pd.read_sql(sql, cnxn)

    X = df.timeDate.values[-20:]
    Y2 = df.volCoin.values[-20:]
    Y = df.volEuro.values[-20:]

    data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Dollers',
                mode= 'lines',
                yaxis='y2',
                line = dict(color = (app_colors['sentiment-plot']),
                            width = 4,)
                )

    data2 = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume',
                marker=dict(color=app_colors['volume-bar']),
                )

    return {'data': [data,data2],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y2),max(Y2*4)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='Dollars'),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)}

@app.callback(Output('price-graph', 'figure'),
              events=[Event('graph-update', 'interval')])
def candle_stick():

    sql2 = "Select * from dbo.BitcoinVal Order BY dateB ,dboTime DESC"
    df2 = pd.read_sql(sql2, cnxn)

    X = df2.timeDate.values[-20:]
    open_data = df2.openingPrice.values[-20:]
    close_data = df2.closePrice.values[-20:]
    low_data = df2.lowPrice.values[-20:]
    high_data = df2.highPrice.values[-20:]

    data = go.Candlestick(
        x=(list(X)),
        open=list(open_data),
        high=list(high_data),
        low=list(low_data),
        close=list(close_data),

            )
    rangeslider= dict(
        visible=False
    )
    return {'data': [data],'layout' : go.Layout(xaxis=dict(rangeslider=dict(visible=False)),
                                                title="CandleStick",
                                                showlegend=False,
                                                font={'color': app_colors['text']},
                                                plot_bgcolor=app_colors['background'],
                                                paper_bgcolor=app_colors['background'],
                                                )}


@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')])
def LstmSent(n_clicks):
    return 'The predicted value is {} '.format(return_prediction2())


@app.callback(
    Output('multi', 'children'),
    [Input('button2', 'n_clicks')])
def LstmSent(n_clicks2):
    return 'The predicted value is {} '.format(return_prediction())






external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})




if __name__ == '__main__':
    app.run_server(debug=True)


