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
    if location.get('results'):
        return location['results'][0]['latitude'], location['results'][0]['longitude']
    return None, None


def get_weather_data(param, longitude, latitude, days):
    params = {
        'Температура': 'temperature_2m',
        'Скорость ветра': 'wind_speed_10m',
        'Вероятность осадков': 'precipitation_probability'
    }
    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly={params[param]}&forecast_days={days}'
    response = requests.get(api_url)
    data = response.json().get('hourly', {})
    return data


def create_figure(data, param):
    df = pd.DataFrame(data)
    fig = go.Figure()
    if param == 'Температура':
        fig.add_trace(go.Scatter(x=df['time'], y=df['temperature_2m'], mode='lines+markers', name='Temperature (°C)'))
        fig.update_layout(title='Hourly Temperature', xaxis_title='Time', yaxis_title='Temperature (°C)')
    elif param == 'Скорость ветра':
        fig.add_trace(go.Scatter(x=df['time'], y=df['wind_speed_10m'], mode='lines+markers', name='Wind Speed (m/s)'))
        fig.update_layout(title='Hourly Wind Speed', xaxis_title='Time', yaxis_title='Wind Speed (m/s)')
    elif param == 'Вероятность осадков':
        fig.add_trace(go.Scatter(x=df['time'], y=df['precipitation_probability'], mode='lines+markers',
                                 name='Precipitation Probability (%)'))
        fig.update_layout(title='Hourly Precipitation Probability', xaxis_title='Time', yaxis_title='Probability (%)')
    return fig


def create_map_figure(locations):
    fig = go.Figure()
    lats, lons = zip(*locations)

    fig.add_trace(go.Scattergeo(
        locationmode='ISO-3',
        lon=lons,
        lat=lats,
        mode='markers+lines',
        marker=dict(size=5, color='red'),
        line=dict(width=2, color='blue')
    ))

    fig.update_layout(
        title='Map Showing Line Between Cities',
        geo=dict(
            showland=True,
            landcolor='rgb(243, 243, 243)',
            subunitcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            showlakes=True,
            showsubunits=True,
            showcountries=True,
            resolution=50,
            projection=dict(type='equirectangular'),
            coastlinecolor='rgb(217, 217, 217)',
            lonaxis=dict(showgrid=True, gridwidth=0.5, range=[-180.0, 180.0], dtick=30),
            lataxis=dict(showgrid=True, gridwidth=0.5, range=[-90.0, 90.0], dtick=30)
        )
    )

    return fig


app = dash.Dash(server=server, routes_pathname_prefix="/dash/", name=__name__)
app.layout = html.Div([
    html.Div([
        dcc.Input(id='city_1', placeholder='Введите название города (на англ)...', type='text', value=''),
        dcc.Input(id='city_2', placeholder='Введите название города (на англ)...', type='text', value=''),
        html.Button('Добавить промежуточный город', id='add-intermediate-button', n_clicks=0),
        html.Button('Submit', id='submit-button', n_clicks=0)
    ], id='input-div'),
    html.Div(id='intermediate-cities', children=[]),
    html.Div(id='output-div', style={'display': 'none'})
])


@app.callback(
    Output('output-div', 'style'),
    Output('output-div', 'children'),
    Input('submit-button', 'n_clicks'),
    State('city_1', 'value'),
    State('city_2', 'value'),
    State('intermediate-cities', 'children')
)
def display_elements(n_clicks, city1, city2, intermediate_cities):
    if n_clicks > 0 and city1 and city2:
        children = []
        children.append(dcc.Dropdown(
            id='weather-parameter-1',
            options=[
                {'label': 'Температура', 'value': 'Температура'},
                {'label': 'Скорость ветра', 'value': 'Скорость ветра'},
                {'label': 'Вероятность осадков', 'value': 'Вероятность осадков'}],
            value='Температура',
            clearable=False))
        children.append(dcc.Slider(1, 7, 1, id='days-counter-1', marks={i: f'Days {i}' for i in range(1, 8)}, value=1))
        children.append(dcc.Graph(id='my-plot-1'))

        children.append(dcc.Dropdown(
            id='weather-parameter-2',
            options=[
                {'label': 'Температура', 'value': 'Температура'},
                {'label': 'Скорость ветра', 'value': 'Скорость ветра'},
                {'label': 'Вероятность осадков', 'value': 'Вероятность осадков'}],
            value='Температура',
            clearable=False))
        children.append(dcc.Slider(1, 7, 1, id='days-counter-2', marks={i: f'Days {i}' for i in range(1, 8)}, value=1))
        children.append(dcc.Graph(id='my-plot-2'))

        for i, input in enumerate(intermediate_cities):
            children.append(dcc.Dropdown(
                id=f'weather-parameter-intermediate-{i}',
                options=[
                    {'label': 'Температура', 'value': 'Температура'},
                    {'label': 'Скорость ветра', 'value': 'Скорость ветра'},
                    {'label': 'Вероятность осадков', 'value': 'Вероятность осадков'}],
                value='Температура',
                clearable=False))
            children.append(
                dcc.Slider(1, 7, 1, id=f'days-counter-intermediate-{i}', marks={j: f'Days {j}' for j in range(1, 8)},
                           value=1))
            children.append(dcc.Graph(id=f'my-plot-intermediate-{i}'))

        children.append(dcc.Graph(id='map-plot'))

        return {'display': 'block'}, children
    return {'display': 'none'}, []


@app.callback(
    Output('intermediate-cities', 'children'),
    Input('add-intermediate-button', 'n_clicks'),
    State('intermediate-cities', 'children')
)
def add_intermediate_city(n_clicks, children):
    if n_clicks > 0:
        new_input = dcc.Input(placeholder='Промежуточный город (на англ)...', type='text', value='')
        children.append(new_input)
    return children


@app.callback(
    Output('my-plot-1', 'figure'),
    Input('weather-parameter-1', 'value'),
    Input('days-counter-1', 'value'),
    State('city_1', 'value')
)
def update_plot_1(param, days, city):
    if city:
        latitude, longitude = get_location(city)
        if latitude is not None and longitude is not None:
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
        if latitude is not None and longitude is not None:
            data = get_weather_data(param, longitude, latitude, days)
            return create_figure(data, param)
    return go.Figure()


@app.callback(
    Output('map-plot', 'figure'),
    Input('city_1', 'value'),
    Input('city_2', 'value'),
    Input('intermediate-cities', 'children')
)
def update_map(city1, city2, intermediate_cities):
    locations = []

    if city1:
        lat1, lon1 = get_location(city1)
        if lat1 is not None and lon1 is not None:
            locations.append((lat1, lon1))

    if city2:
        lat2, lon2 = get_location(city2)
        if lat2 is not None and lon2 is not None:
            locations.append((lat2, lon2))

    for input in intermediate_cities:
        city = input['props']['value']
        if city:
            lat, lon = get_location(city)
            if lat is not None and lon is not None:
                locations.append((lat, lon))

    if locations:
        return create_map_figure(locations)
    return go.Figure()


@app.callback(
    Output({'type': 'my-plot-intermediate', 'index': dash.dependencies.ALL}, 'figure'),
    Input({'type': 'weather-parameter-intermediate', 'index': dash.dependencies.ALL}, 'value'),
    Input({'type': 'days-counter-intermediate', 'index': dash.dependencies.ALL}, 'value'),
    Input('intermediate-cities', 'children')
)
def update_intermediate_plots(params, days, intermediate_cities):
    figures = []
    for i, city_input in enumerate(intermediate_cities):
        city = city_input['props']['value']
        if city:
            latitude, longitude = get_location(city)
            if latitude is not None and longitude is not None:
                data = get_weather_data(params[i], longitude, latitude, days[i])
                figures.append(create_figure(data, params[i]))
            else:
                figures.append(go.Figure())
        else:
            figures.append(go.Figure())
    return figures


if __name__ == '__main__':
    app.run_server(debug=True)