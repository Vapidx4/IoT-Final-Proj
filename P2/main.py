import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import libs.emailSender as EmailSender
import time

temperature = 30
fan_on = False
email_sent = False
wait_time = 300

# Initial temperature values
temp = 25
humidity = 0
fanImg = "assets/img/on.png" if fan_on else "assets/img/off.png"

external_stylesheets = [
    {
        "rel": "stylesheet",
        "href": "assets/styles.css",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True

nav_bar = html.Nav(
    className="col",
    children=[
        html.H2("Nav")
    ]
)


def header(title):
    return html.Header(
        children=html.H2(title)
    )


def gauge(label, unit, minimum, maximum, val=0):
    return html.Div(
        className="block",
        children=daq.Gauge(
            showCurrentValue=True,
            color="#923E8B",
            units=unit,
            value=val,
            label=label,
            max=maximum,
            min=minimum,
        )
    )


# Define layout
app.layout = html.Div(
    className="container",
    children=[
        nav_bar,
        html.Main(
            className="col",
            children=[
                header("IoT Temperature Dashboard"),
                html.Div(
                    className="row",
                    id="main-content",
                    children=[
                        gauge("Temperature", "Celsius", -50, 50, temp),
                        gauge("Humidity", "%", 0, 100, humidity),
                        html.Div(
                            className="col-right",
                            children=[
                            html.Div(
                                className="block",
                                children=[
                                    html.H3(f"Fan Status: {fan_on}"),
                                    html.Img(className="block", src=fanImg)
                                ]
                            )
                            ]
                        )
                    ]
                ),
                # Add Interval component to trigger the callback every 5 seconds
                dcc.Interval(
                    id='interval-component',
                    interval=5 * 1000,  # in milliseconds
                    n_intervals=0
                )
            ]
        ),
    ]
)


# Check for email response every 5 seconds
@app.callback(
    Output('main-content', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update(n):
    global fan_on, email_sent, wait_time

    # Check for email response
    if not email_sent and n % (wait_time / 5) == 0:
        fan_on = EmailSender.main(temperature)
        email_sent = True

    # Update fanImg based on fan_on
    fanImg = "assets/img/on.png" if fan_on else "assets/img/off.png"

    # Update layout
    return [
            gauge("Temperature", "Celsius", -50, 50, temp),
            gauge("Humidity", "%", 0, 100, humidity),
            html.Div(
                className="col-right",
                children=
                    html.Div(
                    className="block col",
                        children=[
                            html.H3(f"Fan Status: {'on' if fan_on else 'off'}"),
                            html.Img(className="block", src=fanImg)
                        ]
                    )
                )
            ]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
