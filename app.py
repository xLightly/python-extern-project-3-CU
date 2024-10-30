import dash
import dash_html_components as html
from dash import dcc, Input, Output
import flask
import pandas as pd
import plotly.graph_objects as go
import requests

server = flask.Flask(__name__)


def get_location(city):
    location_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json'
    response = requests.get(location_url)
    location = response.json()
    return location.get('results',[])[0].get('latitude'),location.get('results',[])[0].get('longitude')


def get_weather_data(param,longitude,latitude,days):
    params={'Температура':'temperature_2m','Скорость ветра':'wind_speed_10m','Вероятность осадков':'precipitation_probability'}
    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly={params[param]}&forecast_days={days}'
    print(api_url)
    response = requests.get(api_url)
    data = response.json().get('hourly', {})
    return data


def create_figure(data,param):
    df = pd.DataFrame(data)
    fig = go.Figure()
    match param:
        case 'Температура':
            fig.add_trace(go.Scatter(x=df['time'],y=df['temperature_2m'], mode='lines+markers', name='Temperature (°C)'))
            fig.update_layout(title='Hourly Temperature', xaxis_title='Time', yaxis_title='Temperature (°C)')
        case 'Скорость ветра':
            fig.add_trace(go.Scatter(x=df['time'],y=df['wind_speed_10m'], mode='lines+markers', name='Wind Speed (m/s)'))
            fig.update_layout(title='Hourly Wind Speed', xaxis_title='Time', yaxis_title='Wind Speed (m/s)')
        case 'Вероятность осадков':
            fig.add_trace(go.Scatter(x=df['time'], y=df['precipitation_probability'], mode='lines+markers',name='Precipitation Probability (%)'))
            fig.update_layout(title='Hourly Precipitation Probability', xaxis_title='Time', yaxis_title='Probability (%)')
    return fig


app = dash.Dash(server=server, routes_pathname_prefix="/dash/")
app.layout = html.Div([
    html.Header('color:red'),
    html.H1("My Dash App with Plotly Graph"),
    dcc.Dropdown(
        id = 'weather-parameter-1',
        options = [
            {'label': 'Температура', 'value': 'Температура'},
            {'label' : 'Скорость ветра','value':'Скорость ветра'},
            {'label' : 'Вероятность осадков', 'value' : 'Вероятность осадков'}],
        value = 'temperature',
        clearable=False),
    dcc.Slider(1,7,1,
            id = 'days-counter-1',
            marks = {i: 'Days{}'.format(i) for i in range(1,8)}),
    dcc.Input(
            id = 'city_1',
            placeholder='Введите название города(на англ)...',
            type='text',
            value=''),
    dcc.Graph(id='my-plot-1'),
    dcc.Dropdown(
        id='weather-parameter-2',
        options=[
            {'label': 'Температура', 'value': 'Температура'},
            {'label': 'Скорость ветра', 'value': 'Скорость ветра'},
            {'label': 'Вероятность осадков', 'value': 'Вероятность осадков'}],
        value='temperature',
        clearable=False),
        dcc.Slider(1,7,1,
            id = 'days-counter-2',
            marks = {i: 'Days{}'.format(i) for i in range(1,8)}),
        dcc.Input(
            id='city_2',
            placeholder='Введите название города(на англ)...',
            type='text',
            value=''),
        dcc.Graph(id='my-plot-2')])


@app.callback(
    Output('my-plot-1', 'figure'),
    Output('my-plot-2','figure'),
    Input('weather-parameter-1', 'value'),
    Input('weather-parameter-2','value'),
    Input('days-counter-1','value'),
    Input('days-counter-2','value'),
    Input('city_1','value'),
    Input('city_2','value'),
    )
def update_graph(selected_parameter_1,selected_parameter_2,days_counter_1,days_counter_2,selected_city_1,selected_city_2):
    latitude_1,longitude_1 = get_location(selected_city_1)
    latitude_2, longitude_2 = get_location(selected_city_2)
    weather_data_1 = get_weather_data(selected_parameter_1, longitude_1, latitude_1, days_counter_1)
    weather_data_2 = get_weather_data(selected_parameter_2, longitude_2, latitude_2, days_counter_2)
    return create_figure(weather_data_1, selected_parameter_1),create_figure(weather_data_2,selected_parameter_2)


if __name__ == "__main__":
    app.run_server(debug=True)