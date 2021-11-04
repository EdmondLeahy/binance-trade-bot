import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
#
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
#
# # LOOK AT THIS : https://www.youtube.com/watch?v=37Zj955LFT0

api_key = 'rxjvvkGRGUcApapeWzUFAvJhHe3lC3doIEbfqL5v75xK4Wwo2H8MiQOoYdx1lwdI'
api_secret_key = 'GFE02ezysvl44wWjdjL05YnpxQqz9lgGir6HEc9rcq10f0cTHSufF6kw98120Btr'

client = Client(api_key, api_secret_key)

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=5000,
            n_intervals=0
        ),
    ]
)



def get_historical_data(length):
    # Calculate the timestamps for the binance api function
    until_this_date = datetime.now()
    since_this_date = until_this_date - timedelta(hours=length)
    # Execute the query from binance - timestamps must be converted to strings !
    candle = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, str(since_this_date),
                                          str(until_this_date))

    # Create a dataframe to label all the columns returned by binance so we work with them later.
    df = pd.DataFrame(candle, columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime',
                                       'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol',
                                       'ignore'])
    # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms')

    # Get rid of columns we do not need
    df = df.drop(['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'],
                 axis=1)

    return df


def add_h_line(fig, data):

    current_price=float(data['low'].iloc[-1])

    fig.add_hline(y=current_price, line_width=3, line_dash="dash", line_color="green",
                  annotation_text=f'{current_price}')
    # fig.update()
    return fig

def make_layout(data, fig):

    first_date = min(data['dateTime'])
    last_date = max(data['dateTime'])
    lowest_val= float(min(data['low']))
    highest_val= float(max(data['high']))

    fig.update_layout(xaxis=dict(range=[first_date, last_date+timedelta(minutes=10)]),
                       yaxis=dict(range=[lowest_val, highest_val]),
                       title=f'{datetime.now()}'
                       )

    return fig


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def graph_update(_):
    candle_data = get_historical_data(1)
    fig = go.Figure(go.Candlestick(x=candle_data['dateTime'],
                          open=candle_data['open'],
                          high=candle_data['high'],
                          low=candle_data['low'],
                          close=candle_data['close']))

    fig = add_h_line(fig, candle_data)
    fig = make_layout(candle_data, fig)

    return fig
#
def run_plot_server():
    app.run_server(debug=True, port=8051)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)