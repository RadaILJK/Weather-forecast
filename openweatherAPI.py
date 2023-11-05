import datetime
import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, State
import requests


df = pd.DataFrame({
    "Data": ["0-0-0", "0-0-0", "0-0-0", "0-0-0", "0-0-0"],
    "Temp": [0, 0, 0, 0, 0],
    "feels_like": [0, 0, 0, 0, 0]})


def get_weather(city):
    weather_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang={'ru'}&appid=KEY&units=metric"
    data = requests.get(weather_url).json()
    if data["cod"] != "404":
        # получаем информацию о погоде на текущий момент
        current_weather = {
            "temperature": data["list"][0]["main"]["temp"],
            "description": data["list"][0]["weather"][0]["description"],
            "icon": f'http://openweathermap.org/img/w/{data["list"][0]["weather"][0]["icon"]}.png',
        }
        # получаем прогноз на 5 дней
        forecast = []
        date = []
        temp = []
        feels_like = []
        for forecast_ in data['list']:
            # мы получаем дату и время именно для этой итерации (для этого forecast)
            date_time = datetime.datetime.strptime(forecast_['dt_txt'], '%Y-%m-%d %H:%M:%S')
            if date_time.hour == 12:
                date.append(date_time.date())
                temp.append(forecast_['main']['temp'])
                feels_like.append(forecast_["main"]["feels_like"])
                forecast.append({
                    "date": date_time.date(),
                    "temperature": forecast_["main"]["temp"],
                    "description": forecast_["weather"][0]["description"],
                    "icon": f'http://openweathermap.org/img/w/{forecast_["weather"][0]["icon"]}.png',
                })

        global df

        df = pd.DataFrame({
            "Data": date,
            "Temp": temp,
            "feels_like": feels_like})

        return current_weather, forecast
    else:
        df = pd.DataFrame({
            "Data": ["0-0-0", "0-0-0", "0-0-0", "0-0-0", "0-0-0"],
            "Temp": [0, 0, 0, 0, 0],
            "feels_like": [0, 0, 0, 0, 0]})
        return None, None


app = dash.Dash(__name__)

central_div = html.Div(
    children=[
        dcc.Dropdown(options=['Temp', 'feels_like'],
                     multi=False,
                     value='Temp',
                     id='slct_group',
                     style={'width': "50%"}
                     ),
        dcc.Graph(figure={}, id='line')],
    style={"display": "flex", "justify-content": "center"},
)

app.layout = html.Div(style={'backgroundColor': 'lightblue'},
                      children=[
        html.H1("Погода в городе"),
        dcc.Input(id="input-city", type="text", placeholder="Введите город"),
        html.Button("Получить данные о погоде", id="btn-weather"),
        html.Div(id="output-weather"),
        central_div
    ]
)


@callback(
    Output("output-weather", "children"),
    [Input("btn-weather", "n_clicks")],
    [State("input-city", "value")],
)
def display_weather(n_clicks, city):
    if n_clicks and city:
        current_weather, forecast = get_weather(city)
        if current_weather and forecast:
            # выводим информацию о погоде на текущий момент
            current_weather_card = html.Div(
                [
                    html.H2(f"Текущая погода в {city}: {current_weather['temperature']}°C"),
                    html.Img(src=current_weather["icon"]),
                    html.P(current_weather["description"]),
                    html.H4('Прогноз погоды на 5 дней:')

                ]
            )

            # выводим прогноз на 5 дней
            forecast_cards = []
            for item in forecast:
                forecast_card = html.Div(
                    [
                        html.H3(f"{item['date']}: {item['temperature']}°C"),
                        html.Img(src=item["icon"]),
                        html.P(item["description"]),
                    ]
                )
                forecast_cards.append(forecast_card)

            return [current_weather_card] + forecast_cards
        else:
            return "Город не найден."


@callback(
    Output(component_id='line', component_property='figure'),
    Input(component_id='slct_group', component_property='value'))
def update_graph(choosen_column):
    fig = px.line(df, x="Data", y=choosen_column, title="5 day forecast", markers=True,
                  width=800, height=500, color_discrete_sequence=['cadetblue'],).update_layout({'plot_bgcolor': 'lightblue',
                                                                                           'paper_bgcolor': 'lightblue'},
                                                                                          xaxis_title="Data",
                                                                                          yaxis_title="Temperature, °C")
    return (fig)


if __name__ == "__main__":
    app.run_server(debug=True)
