import dash
import dash_html_components as html
from dash import dcc, Input, Output, State
import flask
import pandas as pd
import plotly.graph_objects as go
import requests

server = flask.Flask(__name__)

def get_location(city):
    location_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json'
    response = requests.get(location_url)
    location = response.json()
    return location.get('results', [])[0].get('latitude'), location.get('results', [])[0].get('longitude')


def get_weather_data(param, longitude, latitude, days):
    params = {'Температура': 'temperature_2m', 'Скорость ветра': 'wind_speed_10m', 'Вероятность осадков': 'precipitation_probability'}
    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly={params[param]}&forecast_days={days}'
    response = requests.get(api_url)
    data = response.json().get('hourly', {})
    return data


def create_figure(data, param):
    df = pd.DataFrame(data)
    fig = go.Figure()
    match param:
        case 'Температура':
            fig.add_trace(go.Scatter(x=df['time'], y=df['temperature_2m'], mode='lines+markers', name='Temperature (°C)'))
            fig.update_layout(title='Hourly Temperature', xaxis_title='Time', yaxis_title='Temperature (°C)')
        case 'Скорость ветра':
            fig.add_trace(go.Scatter(x=df['time'], y=df['wind_speed_10m'], mode='lines+markers', name='Wind Speed (m/s)'))
            fig.update_layout(title='Hourly Wind Speed', xaxis_title='Time', yaxis_title='Wind Speed (m/s)')
        case 'Вероятность осадков':
            fig.add_trace(go.Scatter(x=df['time'], y=df['precipitation_probability'], mode='lines+markers', name='Precipitation Probability (%)'))
            fig.update_layout(title='Hourly Precipitation Probability', xaxis_title='Time', yaxis_title='Probability (%)')
    return fig


def create_map_figure(lat1, lon1, lat2, lon2):
    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode='ISO-3',
        lon=[lon1, lon2],
        lat=[lat1, lat2],
        mode='markers+lines',
        marker=dict(size=5, color='red'),
        line=dict(width=2, color='blue')
    ))

    fig.update_layout(
        title='Map Showing Line Between Two Cities',
        geo=dict(
            showland=True,
            landcolor='rgb(243, 243, 243)',
            subunitcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            showsubunits=True,
            showcountries=True,
            resolution=50,
            projection=dict(
                type='equirectangular'
            ),
            coastlinecolor='rgb(217, 217, 217)',
            lonaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                range=[-180.0, 180.0],
                dtick=30
            ),
            lataxis=dict(
                showgrid=True,
                gridwidth=0.5,
                range=[-90.0, 90.0],
                dtick=30
            )
        )
    )

    return fig

app = dash.Dash(server=server, routes_pathname_prefix="/dash/", name=__name__)
app.layout = html.Div([
    html.Div([
        dcc.Input(id='city_1', placeholder='Введите название города (на англ)...', type='text', value=''),
        dcc.Input(id='city_2', placeholder='Введите название города (на англ)...', type='text', value=''),
        html.Button('Submit', id='submit-button', n_clicks=0)
    ], id='input-div'),
    html.Div(id='output-div', style={'display': 'none'})
])

@app.callback(
    Output('output-div', 'style'),
    Output('output-div', 'children'),
    Input('submit-button', 'n_clicks'),
    State('city_1', 'value'),
    State('city_2', 'value')
)
def display_elements(n_clicks, city1, city2):
    if n_clicks > 0 and city1 and city2:
        return {'display': 'block'}, [
            dcc.Dropdown(
                id='weather-parameter-1',
                options=[
                    {'label': 'Температура', 'value': 'Температура'},
                    {'label': 'Скорость ветра', 'value': 'Скорость ветра'},
                    {'label': 'Вероятность осадков', 'value': 'Вероятность осадков'}],
                value='Температура',
                clearable=False),
            dcc.Slider(1, 7, 1, id='days-counter-1', marks={i: 'Days{}'.format(i) for i in range(1, 8)}, value=1),
            dcc.Graph(id='my-plot-1'),
            dcc.Dropdown(
                id='weather-parameter-2',
                options=[
                    {'label': 'Температура', 'value': 'Температура'},
                    {'label': 'Скорость ветра', 'value': 'Скорость ветра'},
                    {'label': 'Вероятность осадков', 'value': 'Вероятность осадков'}],
                value='Температура',
                clearable=False),
            dcc.Slider(1, 7, 1, id='days-counter-2', marks={i: 'Days{}'.format(i) for i in range(1, 8)}, value=1),
            dcc.Graph(id='my-plot-2'),
            dcc.Graph(id='map-plot')
        ]
    return {'display': 'none'}, []

@app.callback(
    Output('my-plot-1', 'figure'),
    Input('weather-parameter-1', 'value'),
    Input('days-counter-1', 'value'),
    State('city_1', 'value')
)
def update_plot_1(param, days, city):
    if city:
        latitude, longitude = get_location(city)
        data = get_weather_data(param, longitude, latitude, days)
        return create_figure(data, param)
    return go.Figure()

@app.callback(
    Output('my-plot-2', 'figure'),
    Input('weather-parameter-2', 'value'),
    Input('days-counter-2', 'value'),
    State('city_2', 'value')
)
def update_plot_2(param, days, city):
    if city:
        latitude, longitude = get_location(city)
        data = get_weather_data(param, longitude, latitude, days)
        return create_figure(data, param)
    return go.Figure()

@app.callback(
    Output('map-plot', 'figure'),
    Input('city_1', 'value'),
    Input('city_2', 'value')
)
def update_map(city1, city2):
    if city1 and city2:
        lat1, lon1 = get_location(city1)
        lat2, lon2 = get_location(city2)
        return create_map_figure(lat1, lon1, lat2, lon2)
    return go.Figure()


if __name__ == '__main__':
    app.run_server(debug=True)

