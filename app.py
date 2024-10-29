import dash
import dash_html_components as html
from dash import dcc, Input, Output
import flask
import pandas as pd
import plotly.graph_objects as go
import requests

server = flask.Flask(__name__)

def get_weather_data(param):
    params={'Температура':'temperature_2m','Скорость ветра':'wind_speed_10m','Вероятность осадков':'precipitation_probability'}
    api_url = f'https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly={params[param]}&start_date=2024-10-28&end_date=2024-10-28'
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
    html.H1("My Dash App with Plotly Graph"),
    dcc.Dropdown(
        id = 'weather-parameter',
        options = [
            {'label': 'Температура', 'value': 'Температура'},
            {'label' : 'Скорость ветра','value':'Скорость ветра'},
            {'label' : 'Вероятность осадков', 'value' : 'Вероятность осадков'}],
        value = 'temperature',
        clearable=False),
        dcc.Graph(id='my-plot'), ])

@app.callback(Output('my-plot', 'figure'),Input('weather-parameter', 'value'))
def update_graph(selected_parameter):
    weather_data = get_weather_data(selected_parameter)
    return create_figure(weather_data, selected_parameter)

if __name__ == "__main__":
    app.run_server(debug=True)